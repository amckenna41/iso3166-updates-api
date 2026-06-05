"""
Front-end tests for the ISO 3166 Updates API documentation page (templates/index.html).

Tests use Playwright and require the Flask server to be running.

Install dependencies (once):
    pip install pytest-playwright
    playwright install chromium

Run with:
    BASE_URL=http://127.0.0.1:5000/api python3.10 -m pytest tests/test_frontend.py -v -p no:warnings

The BASE_URL env var matches the existing API test convention; the /api suffix is stripped
automatically to derive the root page URL served at /.
"""

import os
import re

import pytest
from playwright.sync_api import Page, expect


def _page_url() -> str:
    """Derive the root documentation page URL from BASE_URL."""
    base = os.environ.get("BASE_URL", "http://127.0.0.1:5000/api").rstrip("/")
    if base.endswith("/api"):
        base = base[:-4]
    return base + "/"


PAGE_URL = _page_url()


# ---------------------------------------------------------------------------
# Page structure
# ---------------------------------------------------------------------------

class TestPageStructure:
    """Tests for core HTML structure, meta tags, and static elements."""

    def test_page_title(self, page: Page):
        """Page title should reference the ISO 3166 Updates API."""
        page.goto(PAGE_URL)
        expect(page).to_have_title(re.compile(r"ISO 3166 Updates API", re.IGNORECASE))

    def test_meta_charset_utf8(self, page: Page):
        """Page should declare UTF-8 charset."""
        page.goto(PAGE_URL)
        charset = page.locator("meta[charset]").get_attribute("charset")
        assert charset is not None
        assert charset.lower() == "utf-8"

    def test_viewport_meta_present(self, page: Page):
        """Page should include a viewport meta tag for responsive behaviour."""
        page.goto(PAGE_URL)
        viewport = page.locator("meta[name='viewport']")
        expect(viewport).to_be_attached()
        content = viewport.get_attribute("content") or ""
        assert "width=device-width" in content

    def test_left_menu_present(self, page: Page):
        """Left-hand navigation menu should be present and visible."""
        page.goto(PAGE_URL)
        expect(page.locator(".left-menu")).to_be_visible()

    def test_content_page_present(self, page: Page):
        """Main content area should be present and visible."""
        page.goto(PAGE_URL)
        expect(page.locator(".content-page")).to_be_visible()

    def test_theme_toggle_button_present(self, page: Page):
        """Theme toggle button should be present in the DOM (CSS sets display:none)."""
        page.goto(PAGE_URL)
        btn = page.locator(".theme-toggle")
        expect(btn).to_be_attached()
        assert "Switch Theme" in (btn.text_content() or "")

    def test_logo_image_present(self, page: Page):
        """ISO logo image inside the menu should be visible."""
        page.goto(PAGE_URL)
        logo = page.locator(".logo img").first
        expect(logo).to_be_visible()

    def test_github_corner_ribbon_present(self, page: Page):
        """GitHub corner ribbon link should be present."""
        page.goto(PAGE_URL)
        ribbon = page.locator("a.github-corner")
        expect(ribbon).to_be_attached()
        href = ribbon.get_attribute("href") or ""
        assert "github.com/amckenna41" in href


# ---------------------------------------------------------------------------
# Navigation menu
# ---------------------------------------------------------------------------

class TestNavigationMenu:
    """Tests for the left-hand navigation menu items."""

    EXPECTED_MENU_ITEMS = [
        ("content-about",                    "About"),
        ("content-attributes",               "Attributes"),
        ("content-query-string-parameters",  "Query String Parameters"),
        ("content-endpoints",                "Endpoints"),
        ("content-all",                      "All"),
        ("content-code",                     "Alpha Code"),
        ("content-country-name",             "Country Name"),
        ("content-year",                     "Year"),
        ("content-date-range",               "Date Range"),
        ("content-search",                   "Search"),
        ("content-contributing",             "Contributing"),
        ("content-credits",                  "Credits"),
    ]

    def test_menu_item_count(self, page: Page):
        """Navigation menu should contain exactly 12 items."""
        page.goto(PAGE_URL)
        count = page.locator("#section-list-menu li").count()
        assert count == len(self.EXPECTED_MENU_ITEMS), (
            f"Expected {len(self.EXPECTED_MENU_ITEMS)} menu items, got {count}."
        )

    def test_all_menu_items_present(self, page: Page):
        """Every expected menu item should exist with the correct data-target and label."""
        page.goto(PAGE_URL)
        for data_target, label in self.EXPECTED_MENU_ITEMS:
            item = page.locator(f"#section-list-menu li[data-target='{data_target}']")
            expect(item).to_be_attached()
            assert label in (item.text_content() or ""), (
                f"Menu item for '{data_target}' should contain text '{label}'."
            )

    def test_about_item_active_on_load(self, page: Page):
        """The 'About' menu item should be marked active on initial page load."""
        page.goto(PAGE_URL)
        about_item = page.locator("#section-list-menu li[data-target='content-about']")
        expect(about_item).to_have_class(re.compile(r"\bactive\b"))

    def test_clicking_menu_item_sets_active(self, page: Page):
        """Clicking a menu item should add the 'active' class to that item."""
        page.goto(PAGE_URL)
        target_item = page.locator("#section-list-menu li[data-target='content-attributes']")
        target_item.click()
        expect(target_item).to_have_class(re.compile(r"\bactive\b"))

    def test_clicking_menu_item_removes_other_active(self, page: Page):
        """Clicking a menu item should remove 'active' from all other items."""
        page.goto(PAGE_URL)
        page.locator("#section-list-menu li[data-target='content-year']").click()
        for data_target, _ in self.EXPECTED_MENU_ITEMS:
            if data_target == "content-year":
                continue
            item = page.locator(f"#section-list-menu li[data-target='{data_target}']")
            classes = item.get_attribute("class") or ""
            assert "active" not in classes.split(), (
                f"Item '{data_target}' should not be active after clicking 'content-year'."
            )


# ---------------------------------------------------------------------------
# Content sections
# ---------------------------------------------------------------------------

class TestContentSections:
    """Tests that all documented content sections are present in the DOM."""

    EXPECTED_SECTION_IDS = [
        "content-about",
        "content-attributes",
        "content-query-string-parameters",
        "content-endpoints",
        "content-all",
        "content-code",
        "content-country-name",
        "content-year",
        "content-date-range",
        "content-search",
        "content-contributing",
        "content-credits",
    ]

    def test_all_sections_attached(self, page: Page):
        """All expected content sections should be present in the DOM."""
        page.goto(PAGE_URL)
        for section_id in self.EXPECTED_SECTION_IDS:
            expect(page.locator(f"#{section_id}")).to_be_attached()

    def test_about_section_mentions_api(self, page: Page):
        """About section should reference the ISO 3166 Updates API."""
        page.goto(PAGE_URL)
        text = page.locator("#content-about").text_content() or ""
        assert "ISO 3166 Updates API" in text

    def test_attributes_section_lists_four_fields(self, page: Page):
        """Attributes section should list exactly 4 attribute bullet points."""
        page.goto(PAGE_URL)
        items = page.locator("#content-attributes ul li")
        assert items.count() == 4, (
            f"Expected 4 attribute items, got {items.count()}."
        )

    def test_attributes_section_contains_expected_fields(self, page: Page):
        """Attributes section should name all four documented fields."""
        page.goto(PAGE_URL)
        text = page.locator("#content-attributes").text_content() or ""
        for field in ("Change", "Description of Change", "Date Issued", "Source"):
            assert field in text, f"Attributes section missing field: '{field}'."

    def test_query_string_params_section_lists_seven_params(self, page: Page):
        """Query String Parameters section should list exactly 7 parameters."""
        page.goto(PAGE_URL)
        items = page.locator("#content-query-string-parameters ul li")
        assert items.count() == 7, (
            f"Expected 7 query string parameters, got {items.count()}."
        )

    def test_query_string_params_mentions_envelope(self, page: Page):
        """Query String Parameters section should document the response envelope."""
        page.goto(PAGE_URL)
        text = page.locator("#content-query-string-parameters").text_content() or ""
        assert "data" in text
        assert "metadata" in text or "meta" in text

    def test_endpoints_section_heading(self, page: Page):
        """Endpoints section should have an 'Endpoints' heading."""
        page.goto(PAGE_URL)
        expect(page.locator("#content-endpoints h1")).to_contain_text("Endpoints")

    def test_endpoints_section_lists_six_endpoints(self, page: Page):
        """Endpoints section text should mention all 6 main endpoints."""
        page.goto(PAGE_URL)
        text = page.locator("#content-endpoints").text_content() or ""
        for endpoint in ("/all", "/alpha", "/year", "/country_name", "/date_range", "/search"):
            assert endpoint in text, f"Endpoints section missing: '{endpoint}'."

    def test_contributing_section_has_github_link(self, page: Page):
        """Contributing section should contain a link to the GitHub repo."""
        page.goto(PAGE_URL)
        link = page.locator("#content-contributing a[href*='github.com/amckenna41']")
        expect(link).to_be_attached()

    def test_all_content_sections_have_content_section_class(self, page: Page):
        """Every documented section div should carry the 'content-section' class."""
        page.goto(PAGE_URL)
        for section_id in self.EXPECTED_SECTION_IDS:
            classes = page.locator(f"#{section_id}").get_attribute("class") or ""
            assert "content-section" in classes, (
                f"#{section_id} is missing the 'content-section' class."
            )


# ---------------------------------------------------------------------------
# Copy-to-clipboard buttons
# ---------------------------------------------------------------------------

class TestCopyButtons:
    """Tests for the copy-to-clipboard buttons on each endpoint section."""

    EXPECTED_BUTTONS = {
        "copy-text-btn2": "https://iso3166-updates.vercel.app/api/all",
        "copy-text-btn3": "https://iso3166-updates.vercel.app/api/alpha/{input_alpha}",
        "copy-text-btn4": "https://iso3166-updates.vercel.app/api/country_name/{input_country_name}",
        "copy-text-btn5": "https://iso3166-updates.vercel.app/api/year/{input_year}",
        "copy-text-btn6": "https://iso3166-updates.vercel.app/api/date_range/{input_date_range}",
        "copy-text-btn7": "https://iso3166-updates.vercel.app/api/search/{input_search_term}",
    }

    def test_all_copy_buttons_present(self, page: Page):
        """All 6 copy buttons should be present in the DOM."""
        page.goto(PAGE_URL)
        for btn_id in self.EXPECTED_BUTTONS:
            expect(page.locator(f"#{btn_id}")).to_be_attached()

    def test_copy_buttons_have_correct_data_api_url(self, page: Page):
        """Each copy button's data-api-url should match the documented endpoint URL."""
        page.goto(PAGE_URL)
        for btn_id, expected_url in self.EXPECTED_BUTTONS.items():
            actual_url = page.locator(f"#{btn_id}").get_attribute("data-api-url")
            assert actual_url == expected_url, (
                f"Button #{btn_id}: expected data-api-url='{expected_url}', got '{actual_url}'."
            )

    def test_copy_buttons_each_contain_tooltip(self, page: Page):
        """Each copy button should contain a tooltip element."""
        page.goto(PAGE_URL)
        for btn_id in self.EXPECTED_BUTTONS:
            tooltip = page.locator(f"#{btn_id} .tooltip-text")
            expect(tooltip).to_be_attached()

    def test_tooltip_hidden_before_click(self, page: Page):
        """Copy button tooltip should not be visible before the button is clicked."""
        page.goto(PAGE_URL)
        tooltip = page.locator("#copy-text-btn2 .tooltip-text")
        visibility = tooltip.evaluate("el => getComputedStyle(el).visibility")
        assert visibility == "hidden", (
            f"Tooltip should be hidden before click, got visibility='{visibility}'."
        )


# ---------------------------------------------------------------------------
# Theme toggle
# ---------------------------------------------------------------------------

class TestThemeToggle:
    """Tests for the light/dark theme toggle functionality."""

    def test_click_enables_dark_theme(self, page: Page):
        """Invoking toggleTheme() on a light page should add 'dark-theme' to body.

        The .theme-toggle button has display:none in CSS so we call the function
        directly via JS rather than simulating a pointer click.
        """
        page.goto(PAGE_URL)
        page.evaluate("localStorage.removeItem('theme')")
        page.reload()
        page.evaluate("toggleTheme()")
        classes = page.locator("body").get_attribute("class") or ""
        assert "dark-theme" in classes.split()

    def test_click_disables_dark_theme(self, page: Page):
        """Invoking toggleTheme() when dark mode is active should remove 'dark-theme'."""
        page.goto(PAGE_URL)
        page.evaluate("document.body.classList.add('dark-theme')")
        page.evaluate("toggleTheme()")
        classes = page.locator("body").get_attribute("class") or ""
        assert "dark-theme" not in classes.split()

    def test_dark_theme_stored_in_localstorage(self, page: Page):
        """Enabling dark mode via toggleTheme() should persist 'dark' in localStorage."""
        page.goto(PAGE_URL)
        page.evaluate("localStorage.removeItem('theme')")
        page.reload()
        page.evaluate("toggleTheme()")
        stored = page.evaluate("localStorage.getItem('theme')")
        assert stored == "dark", f"Expected localStorage theme='dark', got '{stored}'."

    def test_light_theme_stored_in_localstorage(self, page: Page):
        """Disabling dark mode via toggleTheme() should persist 'light' in localStorage."""
        page.goto(PAGE_URL)
        page.evaluate("document.body.classList.add('dark-theme')")
        page.evaluate("toggleTheme()")
        stored = page.evaluate("localStorage.getItem('theme')")
        assert stored == "light", f"Expected localStorage theme='light', got '{stored}'."

    def test_dark_theme_restored_on_reload(self, page: Page):
        """Dark theme set via localStorage should be applied automatically on page load."""
        page.goto(PAGE_URL)
        page.evaluate("localStorage.setItem('theme', 'dark')")
        page.reload()
        classes = page.locator("body").get_attribute("class") or ""
        assert "dark-theme" in classes.split()

    def test_light_theme_not_applied_when_localstorage_light(self, page: Page):
        """When localStorage theme is 'light', body should not have 'dark-theme'."""
        page.goto(PAGE_URL)
        page.evaluate("localStorage.setItem('theme', 'light')")
        page.reload()
        classes = page.locator("body").get_attribute("class") or ""
        assert "dark-theme" not in classes.split()


# ---------------------------------------------------------------------------
# Version and last-updated elements (async PyPI fetch)
# ---------------------------------------------------------------------------

class TestVersionAndLastUpdated:
    """Tests that version and last-updated elements exist and are populated."""

    def test_version_element_exists(self, page: Page):
        """#version element should be present in the DOM."""
        page.goto(PAGE_URL)
        expect(page.locator("#version")).to_be_attached()

    def test_last_updated_element_exists(self, page: Page):
        """#last-updated element should be present in the DOM."""
        page.goto(PAGE_URL)
        expect(page.locator("#last-updated")).to_be_attached()

    def test_version_element_populated_after_load(self, page: Page):
        """#version should display a version number after page load (async PyPI fetch)."""
        page.goto(PAGE_URL)
        version_elem = page.locator("#version")
        # Wait up to 10 s for the async fetch to complete and populate the element
        page.wait_for_function(
            "() => document.getElementById('version')?.textContent?.trim().length > 0",
            timeout=10000,
        )
        text = version_elem.text_content() or ""
        assert "Version" in text, f"Expected 'Version' in #version text, got: '{text}'."
        assert re.search(r"\d+\.\d+", text), f"No version number found in: '{text}'."

    def test_last_updated_element_populated_after_load(self, page: Page):
        """#last-updated should display a month/year after page load (async PyPI fetch)."""
        page.goto(PAGE_URL)
        page.wait_for_function(
            "() => document.getElementById('last-updated')?.textContent?.trim().length > 0",
            timeout=10000,
        )
        text = page.locator("#last-updated").text_content() or ""
        assert "Last Updated" in text, f"Expected 'Last Updated' in text, got: '{text}'."
        assert re.search(r"\d{4}", text), f"No year found in #last-updated: '{text}'."

    def test_author_element_present(self, page: Page):
        """#author element should be visible and reference 'AJ'."""
        page.goto(PAGE_URL)
        author = page.locator("#author")
        expect(author).to_be_visible()
        assert "AJ" in (author.text_content() or "")


# ---------------------------------------------------------------------------
# Mobile / burger menu
# ---------------------------------------------------------------------------

MOBILE_VIEWPORT = {"width": 375, "height": 667}  # narrower than 680px breakpoint


class TestMobileMenu:
    """Tests for the mobile burger menu toggle.

    The burger icon is only visible at viewport widths <= 680px (CSS media query),
    so each test sets a mobile-sized viewport before interacting.
    """

    def test_burger_button_present(self, page: Page):
        """Burger menu button should be present in the DOM at any viewport size."""
        page.goto(PAGE_URL)
        expect(page.locator("#button-menu-mobile")).to_be_attached()

    def test_burger_button_visible_at_mobile_viewport(self, page: Page):
        """Burger menu button should become visible when viewport is <= 680px wide."""
        page.set_viewport_size(MOBILE_VIEWPORT)
        page.goto(PAGE_URL)
        expect(page.locator("#button-menu-mobile")).to_be_visible()

    def test_burger_click_adds_menu_opened_class(self, page: Page):
        """Clicking the burger button should add 'menu-opened' to <html>."""
        page.set_viewport_size(MOBILE_VIEWPORT)
        page.goto(PAGE_URL)
        page.locator("#button-menu-mobile").click()
        classes = page.locator("html").get_attribute("class") or ""
        assert "menu-opened" in classes.split()

    def test_burger_double_click_removes_menu_opened_class(self, page: Page):
        """Clicking the burger button twice should toggle 'menu-opened' off."""
        page.set_viewport_size(MOBILE_VIEWPORT)
        page.goto(PAGE_URL)
        page.locator("#button-menu-mobile").click()
        page.locator("#button-menu-mobile").click()
        classes = page.locator("html").get_attribute("class") or ""
        assert "menu-opened" not in classes.split()

    def test_mobile_menu_closer_removes_menu_opened_class(self, page: Page):
        """Clicking the mobile-menu-closer should remove 'menu-opened' from <html>."""
        page.set_viewport_size(MOBILE_VIEWPORT)
        page.goto(PAGE_URL)
        page.locator("#button-menu-mobile").click()
        page.locator(".left-menu .mobile-menu-closer").click()
        classes = page.locator("html").get_attribute("class") or ""
        assert "menu-opened" not in classes.split()
