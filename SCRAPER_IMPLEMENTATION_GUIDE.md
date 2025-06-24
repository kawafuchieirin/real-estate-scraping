# Scraper Implementation Guide

This guide explains the current state of the SUUMO and HOMES scrapers and how to complete their implementation.

## Current Status

Both scrapers are **placeholder implementations** that need to be updated with actual website selectors and URL patterns.

### SUUMO Scraper Status
- **URL Generation**: Appears to be correct (`/jj/bukken/ichiran/JJ011FC001/` with query parameters)
- **CSS Selectors**: All selectors are placeholders and need to be updated
- **Expected Elements**: 
  - Property container: `div.property-unit` (placeholder)
  - Price: `.price` (placeholder)
  - Floor plan: `.floor-plan` (placeholder)
  - Area: `.area` (placeholder)
  - Address: `.address` (placeholder)

### HOMES Scraper Status
- **URL Generation**: Returns 404 errors - pattern needs verification
- **Current Pattern**: `/chintai/{property_type}/tokyo/{area_code}/`
- **CSS Selectors**: All selectors are placeholders and need to be updated
- **Expected Elements**:
  - Property container: `div.mod-mergeBuilding` (placeholder)
  - Property link: `.bukkenName` (placeholder)
  - Price: `.priceLabel` (placeholder)
  - Layout: `.layout` (placeholder)

## How to Complete Implementation

### Step 1: Verify URL Patterns

1. **SUUMO**:
   ```
   1. Visit https://suumo.jp
   2. Search for rental properties in Tokyo (e.g., Shibuya-ku)
   3. Note the actual URL structure
   4. Update the URL pattern if needed
   ```

2. **HOMES**:
   ```
   1. Visit https://www.homes.co.jp
   2. Search for rental properties in Tokyo
   3. Note the actual URL structure
   4. Update the URL pattern in homes.py line 46
   ```

### Step 2: Inspect HTML Structure

1. Open browser developer tools (F12)
2. Use the element inspector to find:
   - The container element for each property listing
   - CSS classes/IDs for price, area, address, etc.
   - Any data attributes that contain property information

### Step 3: Update Selectors

Replace placeholder selectors with actual ones found from inspection:

```python
# Example for SUUMO
# Instead of:
property_items = soup.find_all('div', class_='property-unit')

# Use actual selector:
property_items = soup.find_all('div', class_='actual-class-name')
```

### Step 4: Test Implementation

1. Run the scraper with debug logging:
   ```bash
   python -m src.main --areas 13113 --property-types apartment
   ```

2. Verify that properties are being found and parsed correctly

3. Check that all required fields are being extracted

### Step 5: Handle Edge Cases

Consider and handle:
- Missing fields (some properties may not have all information)
- Different property types (apartment vs house)
- Pagination edge cases
- Rate limiting and robots.txt compliance

## Important Notes

1. **Respect robots.txt**: The scrapers already check robots.txt compliance
2. **Rate Limiting**: Already implemented (10 requests per 60 seconds)
3. **Error Handling**: Basic error handling is in place but may need enhancement
4. **Data Validation**: Consider adding validation for extracted data

## Testing Your Implementation

After updating the selectors:

```bash
# Test single area
python -m src.main --areas 13113 --property-types apartment

# Test multiple areas
python -m src.main --areas 13113 13104 --property-types apartment

# Test with different export formats
python -m src.main --areas 13113 --export-format json
```

## Need Help?

If you encounter issues:
1. Check the logs for detailed error messages
2. Verify robots.txt compliance
3. Ensure selectors match current website structure
4. Test with smaller datasets first