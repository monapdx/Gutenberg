[![How-To](https://img.shields.io/badge/%F0%9F%93%8CHow%20To-111111?style=for-the-badge)](#how-to) [![Politics](https://img.shields.io/badge/%E2%9C%8APolitics-111111?style=for-the-badge)](#politics) [![Art](https://img.shields.io/badge/%F0%9F%8E%A8Art-111111?style=for-the-badge)](#art) [![Cooking & Drinking](https://img.shields.io/badge/%F0%9F%94%A5Cooking%20%26%20Drinking-111111?style=for-the-badge)](#cooking--drinking) [![Economics](https://img.shields.io/badge/%F0%9F%92%B0Economics-111111?style=for-the-badge)](#economics) [![Health & Medicine](https://img.shields.io/badge/%F0%9F%92%8AHealth%20%26%20Medicine-111111?style=for-the-badge)](#health--medicine) [![Engineering & Technology](https://img.shields.io/badge/%E2%9A%99%EF%B8%8FEngineering%20%26%20Technology-111111?style=for-the-badge)](#engineering--technology) [![Novels](https://img.shields.io/badge/%F0%9F%93%96Novels-111111?style=for-the-badge)](#novels) [![History](https://img.shields.io/badge/%F0%9F%8F%BAHistory-111111?style=for-the-badge)](#history) [![Business](https://img.shields.io/badge/%F0%9F%92%B2Business-111111?style=for-the-badge)](#business) [![Mythology & Folklore](https://img.shields.io/badge/%F0%9F%AA%BDMythology-111111?style=for-the-badge)](#mythology--folklore) [![Psychology](https://img.shields.io/badge/%F0%9F%94%8DPsychology-111111?style=for-the-badge)](#psychology) 

<img src="https://raw.githubusercontent.com/monapdx/Gutenberg/refs/heads/main/main.png">

<img src="https://raw.githubusercontent.com/monapdx/Gutenberg/refs/heads/main/category-page.png">

## Data format

Category files are stored in `data/` as JSON arrays.
Each file contains a list of objects (one object per row).

For this project, a normal book row uses these fields:

- `link href`: URL to the Gutenberg ebook page
- `cover-thumb src`: URL to the small cover image
- `title`: book title
- `subtitle`: author name (or short secondary text)
- `extra`: download text such as `4075 downloads`

Notes:

- The generator reads only rows that look like book rows.
- Rows used for pagination or other metadata are ignored.
- Keeping all five fields makes output pages more complete.

### Example JSON entry

```json
{
  "link href": "https://gutenberg.org/ebooks/11",
  "cover-thumb src": "https://gutenberg.org/cache/epub/11/pg11.cover.small.jpg",
  "title": "Alice's Adventures in Wonderland",
  "subtitle": "Lewis Carroll",
  "extra": "54955 downloads"
}
```

## Add a new category

1. Create a new JSON file in `data/`.
2. Name it with a clean slug, for example `science-fiction.json`.
3. Add a JSON array (`[]`) and place one book object per item using the format above.
4. Run the site build command:

	```bash
	python build_site.py
	```

5. Check the generated pages:
	- `site/index.html` includes the new category
	- `site/categories/` contains the new category page





