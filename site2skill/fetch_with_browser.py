
import os
import time
import logging
import urllib.parse
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

def sanitize_filename(name: str) -> str:
    """
    Sanitize a string to be safe for filenames.
    Replaces special characters with underscores.
    """
    # Characters invalid in Windows filenames
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name

def get_save_path(url: str, crawl_dir: str) -> str:
    """
    Determine the local save path for a given URL.
    Handles query parameters by incorporating them into the filename.
    """
    parsed = urllib.parse.urlparse(url)
    domain = parsed.netloc
    path = parsed.path
    if path.startswith('/'):
        path = path[1:]
    
    # If path is empty (root), use index.html
    if not path:
        path = "index.html"
    elif path.endswith('/'):
        path += "index.html"
        
    # Handle query parameters
    if parsed.query:
        # Append query params to filename, replacing ? and & with _
        # e.g. path/to/file.html?guid=123 -> path/to/file_guid_123.html
        
        # Split extension if present
        root, ext = os.path.splitext(path)
        if not ext:
            ext = ".html" # Default to html if no extension
            
        sanitized_query = sanitize_filename(parsed.query)
        path = f"{root}_{sanitized_query}{ext}"
    else:
         # Ensure extension
        root, ext = os.path.splitext(path)
        if not ext:
            path += ".html"

    return os.path.join(crawl_dir, domain, path)


def fetch_site_with_browser(url: str, output_dir: str, sidebar_selector: str = None) -> None:
    """
    Fetch a site using a browser (Playwright).
    
    Args:
        url: The entry point URL.
        output_dir: The directory to save content.
        sidebar_selector: CSS selector for the sidebar to extract links from.
    """
    crawl_dir = os.path.join(output_dir, "crawl")
    if not os.path.exists(crawl_dir):
        os.makedirs(crawl_dir)

    logger.info(f"Starting browser fetch for {url}")
    logger.info(f"Sidebar selector: {sidebar_selector}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use a standard Chrome User Agent to avoid being blocked/served 404s
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 site2skill/0.1"
        context = browser.new_context(
             user_agent=ua
        )
        page = context.new_page()

        try:
            logger.info("Navigating to entry page...")
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            # Wait for sidebar if selector is provided
            if sidebar_selector:
                try:
                    page.wait_for_selector(sidebar_selector, timeout=10000)
                except Exception:
                    logger.warning(f"Sidebar selector '{sidebar_selector}' not found or timed out. Proceeding with what we have.")

            # Extract links
            links_to_visit = set()
            
            # Always add the entry URL
            links_to_visit.add(url)
            
            # Extract links
            links_to_visit = set()
            
            # Always add the entry URL
            links_to_visit.add(url)
            
            if sidebar_selector:
                logger.info(f"Extracting links from sidebar: {sidebar_selector}")
                
                # Helper to find element in frames
                target_frame = None
                sidebar_element = page.query_selector(sidebar_selector)
                
                if sidebar_element:
                    target_frame = page.main_frame
                else:
                    # Check frames
                    for frame in page.frames:
                        try:
                            if frame.query_selector(sidebar_selector):
                                target_frame = frame
                                logger.info(f"Found sidebar in frame: {frame.name or frame.url}")
                                break
                        except Exception:
                            continue
                            
                if target_frame:
                    # Recursive expansion logic
                    logger.info("Starting recursive sidebar expansion...")
                    last_link_count = 0
                    max_passes = 10 # Safety limit
                    
                    for pass_idx in range(max_passes):
                        # Count current visible links
                        current_links = target_frame.query_selector_all(f"{sidebar_selector} a")
                        current_count = len(current_links)
                        logger.info(f"Expansion Pass {pass_idx+1}: {current_count} links found.")
                        
                        if current_count == last_link_count and pass_idx > 0:
                            logger.info("No new links found. Expansion complete.")
                            break
                        
                        last_link_count = current_count
                        
                        # Find expandable items
                        # Strategy: Look for images with 'arrowright' or similar indicators commonly used in Doxygen/Treeviews
                        # or elements with aria-expanded="false" if available (though browser check showed strict img src usage)
                        # We will try to click all 'closed' indicators.
                        
                        # Find images acting as expand buttons (commonly arrows pointing right)
                        # We specifically target images inside links usually
                        expand_buttons = target_frame.query_selector_all(f"{sidebar_selector} img")
                        clicked_any = False
                        
                        for img in expand_buttons:
                            src = img.get_attribute('src') or ""
                            # Doxygen and similar systems often use 'arrowright', 'closed', 'plus' for closed nodes
                            if any(k in src.lower() for k in ['arrowright', 'closed.png', 'folderclosed']):
                                try:
                                    # Check if visible
                                    if img.is_visible():
                                        # Click the parent anchor or the image itself
                                        parent = img.query_selector('xpath=..') # Get parent
                                        if parent and parent.evaluate('el => el.tagName === "A"', parent):
                                            parent.click()
                                        else:
                                            img.click()
                                            
                                        # Small wait for animation/DOM update
                                        page.wait_for_timeout(200) 
                                        clicked_any = True
                                except Exception:
                                    pass # Ignore click errors
                        
                        if not clicked_any:
                            logger.info("No expandable items found or clickable.")
                            break
                            
                        # Wait a bit more after a batch of clicks
                        page.wait_for_timeout(1000)

                    # Re-query anchors after expansion
                    anchors = target_frame.query_selector_all(f"{sidebar_selector} a")
                    logger.info(f"Found {len(anchors)} anchors in sidebar after expansion.")
                    for a in anchors:
                        href = a.get_attribute('href')
                        if href:
                            # Resolve relative URLs using the frame's URL base
                            full_url = urllib.parse.urljoin(target_frame.url, href)
                            
                            # Filter
                            parsed_full = urllib.parse.urlparse(full_url)
                            if parsed_full.scheme in ('http', 'https'):
                                # Strip fragment (#section) to avoid duplicate fetches
                                full_url_no_frag = urllib.parse.urldefrag(full_url).url
                                links_to_visit.add(full_url_no_frag)
                else:
                    logger.warning(f"Sidebar selector '{sidebar_selector}' not found in any frame.")

            logger.info(f"Found {len(links_to_visit)} unique links to process.")

            # Identify domain to restrict crawl scope if we were doing recursive, but here we just list visited
            # For this simplified implementation, we just visit the list we found.
            
            visited_urls = set()
            
            total = len(links_to_visit)
            for i, link in enumerate(sorted(links_to_visit)):
                if link in visited_urls:
                    continue
                
                logger.info(f"[{i+1}/{total}] Processing: {link}")
                
                try:
                    # We might reuse the page or create new ones. Reusing is faster but can accumulate state.
                    # For stability, let's reuse but handle errors.
                    page.goto(link, wait_until="networkidle", timeout=30000)
                    
                    # Wait a bit for dynamic content?
                    # page.wait_for_timeout(1000) 
                    
                    # Handle Autodesk's Iframe-based content loading
                    content_frame_selector = "#ui-content-frame"
                    content = ""
                    
                    try:
                        # Check if the specific content iframe exists and is visible/attached
                        iframe_element = page.query_selector(content_frame_selector)
                        if iframe_element:
                            logger.info(f"Detected content iframe '{content_frame_selector}'. Waiting for it to load...")
                            content_frame = iframe_element.content_frame()
                            if content_frame:
                                # Wait for the frame to have some content or reach a loaded state
                                # Simply waiting for load state might be enough, or wait for a specific element inside if known.
                                # For generic usage, we wait for load.
                                try:
                                    content_frame.wait_for_load_state("domcontentloaded", timeout=30000)
                                    # Optional: Wait a small amount strictly for JS to settle if needed
                                    page.wait_for_timeout(2000) 
                                    content = content_frame.content()
                                    logger.info("Successfully captured content from iframe.")
                                except Exception as e:
                                    logger.warning(f"Timeout or error waiting for iframe load: {e}. Falling back to page content.")
                                    content = page.content()
                            else:
                                content = page.content()
                        else:
                            content = page.content()
                    except Exception as e:
                        logger.warning(f"Error trying to handle iframe: {e}. Falling back to default.")
                        content = page.content()

                    # Save contents
                    save_path = get_save_path(link, crawl_dir)
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    
                    with open(save_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                        
                    visited_urls.add(link)
                    
                except Exception as e:
                    logger.error(f"Failed to fetch {link}: {e}")
                    # Continue to next link

        except Exception as e:
            logger.error(f"Top level browser error: {e}")
        finally:
            browser.close()
            
    logger.info(f"Browser fetch complete. Processed {len(visited_urls)} pages.")
