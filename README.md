# WidgetCraft template library

Editable WidgetCraft templates and previews, grouped by design category. The initial collection contains62 templates:35 Studio originals and27 designs across Brutalist, Minimalist, Editorial, Bauhaus, Retro Pixel, Art Deco and Soft Pastel.

## Add a widget

1. Export an editable `.widget.json` from WidgetCraft.
2. Add it to a category folder, for example `minimalist/my-clock.widget.json`.
3. Optionally add a matching PNG preview, `minimalist/my-clock.png`. Without a preview, people can download the template and see it in the editor.
4. Commit to `main`. The **Update template catalogue** GitHub Actions workflow validates the files and updates `catalog.json` automatically.
5. Tap **Refresh** in the app's online template library. New designs and categories do not require a new app release. GitHub's public-file cache can delay a change briefly.

## Add a category

Create a new folder with a template inside it. The folder name becomes its display category. For a custom label/order, add `category.json` inside that folder:

```json
{"name":"My new style","order":50}
```

The app reads category names from the catalogue. No hard-coded app category list needs changing. Empty folders do not appear until a template is added. New widget engine features or document formats still require app support.

## File limits

Use simple ASCII folder/file names with letters,numbers,hyphens or underscores. Keep each portable document below4MiB,within48..800 logical pixels per side and40layers. Keep PNG previews below2MiB and2048pixels per side. The catalogue supports up to500templates and60categories. Embedded image/font assets must retain their SHA-256 keys. The build script uses only Python's standard library.

## Offline use and integrity

The app verifies downloaded byte counts,SHA-256 hashes and the document itself before saving a private offline copy. Choosing a template creates an independent editable widget. Removing a template download leaves saved widgets unchanged. A small starter set remains bundled for first use without internet. The catalogue and previews are fetched from public GitHub files,with no GitHub token embedded in the app.

Previews use example data. Optional weather,fitness,calendar,media and local connections require their normal setup/permissions. Mood,initials,reading-page counts,quotes and vocabulary are authored examples; automatic mood sensing or dictionary services are not claimed. The portrait is fictional,previously generated/reviewed artwork. Initial previews are actual WidgetCraft renderer exports,not screenshots of the editor.

Font notices are in `licenses/`. This is a public/free template catalogue: uploaded files are publicly downloadable. Do not upload personal widget data,credentials,keys or private assets.
