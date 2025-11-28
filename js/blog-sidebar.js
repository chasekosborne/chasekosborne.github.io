/**
 * Blog Post Sidebar Navigation
 * 
 * Auto-generates a hierarchical navigation sidebar for blog posts based on h1, h2, and h3 headers.
 * Features:
 * - Automatically assigns IDs to headers without them
 * - Builds hierarchical navigation structure
 * - Smooth scroll to sections on click
 * - Active section highlighting based on scroll position
 * - Sticky/fixed positioning after initial scroll
 * - Collapsible nested sections
 * - Responsive design (hides on mobile)
 * - Gracefully hides if fewer than 2 headers found
 * 
 * Usage:
 * Simply include this script in your blog post HTML. The sidebar will be automatically
 * generated and inserted into a container with id="blog-sidebar-container".
 * 
 * HTML Structure Required:
 * - A container with id="blog-sidebar-container" (will be created if not present)
 * - Article content within an element with class "article" or id="article-content"
 */

(function() {
    'use strict';

    // Configuration
    const CONFIG = {
        headerSelectors: ['h1', 'h2', 'h3'],
        sidebarContainerId: 'blog-sidebar-container',
        articleSelector: '.article',
        stickyOffset: 20, // Offset from top when sticky
        scrollOffset: 80, // Offset for scroll positioning
        minHeaders: 2, // Minimum headers required to show sidebar
        activeClass: 'active',
        collapsedClass: 'collapsed'
    };

    /**
     * Generate a URL-friendly ID from text
     */
    function generateId(text) {
        return text
            .toLowerCase()
            .trim()
            .replace(/[^\w\s-]/g, '') // Remove special characters
            .replace(/\s+/g, '-') // Replace spaces with hyphens
            .replace(/-+/g, '-') // Replace multiple hyphens with single
            .replace(/^-|-$/g, ''); // Remove leading/trailing hyphens
    }

    /**
     * Get header level (1, 2, or 3)
     */
    function getHeaderLevel(header) {
        const tagName = header.tagName.toLowerCase();
        return parseInt(tagName.replace('h', ''));
    }

    /**
     * Collect all headers from the article and assign IDs
     */
    function collectHeaders() {
        const article = document.querySelector(CONFIG.articleSelector);
        if (!article) {
            console.warn('Blog sidebar: Article element not found');
            return [];
        }

        const headers = Array.from(article.querySelectorAll(CONFIG.headerSelectors.join(', ')))
            .filter(header => {
                // Skip headers in front-matter or other non-content areas
                const frontMatter = header.closest('.front-matter');
                return !frontMatter;
            });

        // Assign IDs to headers that don't have them
        headers.forEach(header => {
            if (!header.id) {
                const text = header.textContent || header.innerText;
                let id = generateId(text);
                
                // Ensure uniqueness
                let counter = 1;
                let uniqueId = id;
                while (document.getElementById(uniqueId)) {
                    uniqueId = `${id}-${counter}`;
                    counter++;
                }
                
                header.id = uniqueId;
            }
        });

        return headers.map(header => ({
            element: header,
            id: header.id,
            text: header.textContent || header.innerText,
            level: getHeaderLevel(header)
        }));
    }

    /**
     * Build hierarchical navigation structure
     */
    function buildNavStructure(headers) {
        if (headers.length === 0) return null;

        const structure = [];
        const stack = []; // Stack to track parent items

        headers.forEach(header => {
            const item = {
                id: header.id,
                text: header.text,
                level: header.level,
                element: header.element,
                children: []
            };

            // Pop stack until we find the appropriate parent
            while (stack.length > 0 && stack[stack.length - 1].level >= header.level) {
                stack.pop();
            }

            if (stack.length === 0) {
                // Top-level item
                structure.push(item);
            } else {
                // Child of the top item on stack
                stack[stack.length - 1].children.push(item);
            }

            stack.push(item);
        });

        return structure;
    }

    /**
     * Create sidebar HTML from navigation structure
     */
    function createSidebarHTML(structure) {
        function createList(items, isRoot = false) {
            if (items.length === 0) return '';

            const listClass = isRoot ? 'blog-sidebar-nav' : 'blog-sidebar-nav-nested';
            let html = `<ul class="${listClass}">`;

            items.forEach(item => {
                const hasChildren = item.children.length > 0;
                const toggleClass = hasChildren ? 'blog-sidebar-toggle' : '';
                const childrenHTML = hasChildren ? createList(item.children) : '';

                html += `
                    <li class="blog-sidebar-item" data-level="${item.level}">
                        <a href="#${item.id}" 
                           class="blog-sidebar-link ${toggleClass}" 
                           data-id="${item.id}">
                            ${item.text}
                        </a>
                        ${childrenHTML}
                    </li>
                `;
            });

            html += '</ul>';
            return html;
        }

        return `
            <nav class="blog-sidebar" id="blog-sidebar">
                <div class="blog-sidebar-header">Contents</div>
                ${createList(structure, true)}
            </nav>
        `;
    }

    /**
     * Smooth scroll to element
     */
    function scrollToElement(element) {
        const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
        const offsetPosition = elementPosition - CONFIG.scrollOffset;

        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });
    }

    /**
     * Get the currently visible section based on scroll position
     */
    function getActiveSection(headers) {
        const scrollPosition = window.pageYOffset + CONFIG.scrollOffset + 10;

        // Find the last header that's above the scroll position
        let activeHeader = null;
        for (let i = headers.length - 1; i >= 0; i--) {
            const header = headers[i];
            const headerTop = header.element.getBoundingClientRect().top + window.pageYOffset;
            
            if (headerTop <= scrollPosition) {
                activeHeader = header;
                break;
            }
        }

        return activeHeader;
    }

    /**
     * Update active state in sidebar
     */
    function updateActiveState(activeHeader, sidebar) {
        if (!sidebar) return;

        // Remove all active classes
        sidebar.querySelectorAll('.blog-sidebar-link').forEach(link => {
            link.classList.remove(CONFIG.activeClass);
        });

        // Add active class to current section
        if (activeHeader) {
            const activeLink = sidebar.querySelector(`[data-id="${activeHeader.id}"]`);
            if (activeLink) {
                activeLink.classList.add(CONFIG.activeClass);
                
                // Expand parent sections if needed
                let parent = activeLink.closest('.blog-sidebar-item');
                while (parent) {
                    const nestedList = parent.querySelector('.blog-sidebar-nav-nested');
                    if (nestedList) {
                        parent.classList.remove(CONFIG.collapsedClass);
                    }
                    parent = parent.parentElement?.closest('.blog-sidebar-item');
                }
            }
        }
    }

    /**
     * Attach click handlers to sidebar links
     */
    function attachClickHandlers(sidebar, headers) {
        sidebar.querySelectorAll('.blog-sidebar-link').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const targetId = this.getAttribute('data-id');
                const header = headers.find(h => h.id === targetId);
                
                if (header) {
                    scrollToElement(header.element);
                    updateActiveState(header, sidebar);
                }
            });
        });

        // Toggle nested sections
        sidebar.querySelectorAll('.blog-sidebar-toggle').forEach(toggle => {
            toggle.addEventListener('click', function(e) {
                const item = this.closest('.blog-sidebar-item');
                if (item) {
                    item.classList.toggle(CONFIG.collapsedClass);
                }
            });
        });
    }

    /**
     * Handle scroll events for active section tracking
     */
    function attachScrollListeners(sidebar, headers) {
        let ticking = false;

        function updateOnScroll() {
            const activeHeader = getActiveSection(headers);
            updateActiveState(activeHeader, sidebar);
            ticking = false;
        }

        window.addEventListener('scroll', function() {
            if (!ticking) {
                window.requestAnimationFrame(updateOnScroll);
                ticking = true;
            }
        }, { passive: true });

        // Initial update
        updateOnScroll();
    }

    /**
     * Initialize sticky positioning
     * Positions sidebar aligned with Introduction header initially,
     * then sticks to top when scrolled past it
     */
    function initStickySidebar(sidebar) {
        if (!sidebar) return;

        const sidebarContainer = sidebar.parentElement;
        if (!sidebarContainer) return;

        // Find the Introduction header
        const introHeader = document.getElementById('introduction');
        if (!introHeader) {
            console.warn('Blog sidebar: Introduction header not found, using default positioning');
            return;
        }

        let initialTop = null;
        let initialLeft = null;
        let stickyThreshold = null;
        let stickyLeft = null;

        function calculatePositions() {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const content = sidebarContainer.closest('.content');
            const article = document.querySelector(CONFIG.articleSelector);
            
            // Get positions relative to viewport
            const introRect = introHeader.getBoundingClientRect();
            const contentRect = content?.getBoundingClientRect();
            const articleRect = article?.getBoundingClientRect();
            
            // Calculate positions relative to document
            const introTop = introRect.top + scrollTop;
            const contentTop = contentRect ? (contentRect.top + scrollTop) : 0;
            
            // Calculate position of Introduction header relative to content container
            // This is what we'll use for the absolute positioning
            initialTop = introTop - contentTop;
            
            // Calculate left position to be in the left margin (outside the article)
            // Article is centered with max-width 700px, so left margin = (viewport width - 700px) / 2
            // Position sidebar in the left margin, with some padding from the edge
            const viewportWidth = window.innerWidth;
            const articleWidth = 700; // max-width of article
            const leftMarginWidth = (viewportWidth - articleWidth) / 2;
            
            // Position in left margin with padding (e.g., 20px from left edge, or center of margin if too narrow)
            const sidebarWidth = 220;
            const padding = 20;
            
            let leftPositionFromViewport;
            if (leftMarginWidth > sidebarWidth + padding * 2) {
                // Enough space: position with padding from left edge
                leftPositionFromViewport = padding;
            } else if (leftMarginWidth > sidebarWidth) {
                // Some space: center in available margin
                leftPositionFromViewport = (leftMarginWidth - sidebarWidth) / 2;
            } else {
                // Not enough space: position at left edge of viewport
                leftPositionFromViewport = 0;
            }
            
            // For absolute positioning, left is relative to content container
            // For fixed positioning, left is relative to viewport
            // Account for content container's position relative to viewport
            if (contentRect) {
                const contentLeft = contentRect.left;
                // initialLeft is relative to content container, stickyLeft is relative to viewport
                initialLeft = leftPositionFromViewport - contentLeft;
                stickyLeft = leftPositionFromViewport;
            } else {
                // Fallback: assume content is at viewport edge
                initialLeft = leftPositionFromViewport;
                stickyLeft = leftPositionFromViewport;
            }
            
            // Threshold: when Introduction header reaches near the top of viewport
            // We want to stick when scrolled past this point
            stickyThreshold = introTop - CONFIG.stickyOffset;
        }

        function updateSticky() {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            
            // Recalculate positions if not yet calculated
            if (initialTop === null || stickyThreshold === null) {
                calculatePositions();
            }

            // Check if we've scrolled past the Introduction header
            if (scrollTop >= stickyThreshold) {
                // Stick to top
                sidebarContainer.classList.add('sticky');
                sidebar.classList.add('blog-sidebar-sticky');
                sidebarContainer.style.top = ''; // Clear inline top when sticky
                sidebarContainer.style.left = `${stickyLeft}px`; // Set left position for sticky
            } else {
                // Return to original position aligned with Introduction
                sidebarContainer.classList.remove('sticky');
                sidebar.classList.remove('blog-sidebar-sticky');
                sidebarContainer.style.top = `${initialTop}px`;
                sidebarContainer.style.left = `${initialLeft}px`; // Set left position for absolute
            }
        }

        // Calculate initial positions
        calculatePositions();
        
        // Set initial position
        if (initialTop !== null) {
            sidebarContainer.style.top = `${initialTop}px`;
        }
        if (initialLeft !== null) {
            sidebarContainer.style.left = `${initialLeft}px`;
        }

        // Update on scroll
        window.addEventListener('scroll', function() {
            updateSticky();
        }, { passive: true });

        // Recalculate on resize
        let resizeTimeout;
        window.addEventListener('resize', function() {
            // Debounce resize events
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(function() {
                calculatePositions();
                updateSticky();
            }, 100);
        }, { passive: true });

        // Initial check
        updateSticky();
    }

    /**
     * Create sidebar container if it doesn't exist
     */
    function ensureSidebarContainer() {
        let container = document.getElementById(CONFIG.sidebarContainerId);
        
        if (!container) {
            container = document.createElement('div');
            container.id = CONFIG.sidebarContainerId;
            container.className = 'blog-sidebar-container';
            
            // Insert at the beginning of the content area, before article
            const content = document.querySelector('.content');
            const article = document.querySelector(CONFIG.articleSelector);
            
            if (content) {
                if (article && article.parentElement === content) {
                    content.insertBefore(container, article);
                } else {
                    content.insertBefore(container, content.firstChild);
                }
            } else if (article && article.parentElement) {
                article.parentElement.insertBefore(container, article);
            } else {
                document.body.appendChild(container);
            }
        }
        
        return container;
    }

    /**
     * Main initialization function
     */
    function init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }

        // Collect headers
        const headers = collectHeaders();

        // Hide sidebar if not enough headers
        if (headers.length < CONFIG.minHeaders) {
            console.log(`Blog sidebar: Only ${headers.length} headers found, minimum ${CONFIG.minHeaders} required. Sidebar hidden.`);
            const container = document.getElementById(CONFIG.sidebarContainerId);
            if (container) {
                container.classList.remove('active');
            }
            return;
        }

        console.log(`Blog sidebar: Found ${headers.length} headers, generating sidebar...`);

        // Build navigation structure
        const navStructure = buildNavStructure(headers);
        if (!navStructure || navStructure.length === 0) {
            return;
        }

        // Create sidebar container
        const container = ensureSidebarContainer();
        
        // Generate and insert sidebar HTML
        const sidebarHTML = createSidebarHTML(navStructure);
        container.innerHTML = sidebarHTML;
        
        // Add active class to show sidebar (CSS will handle responsive hiding)
        container.classList.add('active');

        const sidebar = document.getElementById('blog-sidebar');
        if (!sidebar) return;

        // Attach event handlers
        attachClickHandlers(sidebar, headers);
        attachScrollListeners(sidebar, headers);
        initStickySidebar(sidebar);

        // Set initial active state
        const activeHeader = getActiveSection(headers);
        updateActiveState(activeHeader, sidebar);
    }

    // Initialize
    init();
})();


