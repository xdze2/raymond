# Wikis

A multi-wiki repo. Each wiki under `wikis/<name>/` is a self-contained TVTropes-style reference work with its own axes, catalogue, pages, prompts, and frontend.

See [project_vision.md](project_vision.md) for the concept behind the data_atlas wiki.

## Layout

```
wikis/
  data_atlas/
    wiki.json          # title, wordmark, axes used by gen_list.sh, extra chips
    axis.json          # axis definitions (id, label, values)
    catalogue/         # JSONL files of candidate entries + index.json
    pages/             # full prose markdown entries + index.json
    prompts/           # make_list.txt, make_page.txt (per-wiki framing)
    frontend/          # index.html, style.css (one deployment per wiki)
  mobility_innov/
    ...
gen_list.sh            # generate a catalogue file via Claude CLI
update_index.sh        # rebuild catalogue/index.json after adding files
```

## Run a wiki locally

```bash
python3 -m http.server 8765
```

Then open:

- data_atlas: <http://localhost:8765/wikis/data_atlas/frontend/index.html>
- mobility_innov: <http://localhost:8765/wikis/mobility_innov/frontend/index.html>

No build step. The files are the site.

## Generate catalogue entries

```bash
# positional args = values for wiki.json's gen_axes, then freeform_axes
./gen_list.sh data_atlas sensor buried individual medical
./update_index.sh data_atlas
```

`gen_list.sh` reads `wikis/<wiki>/wiki.json` to know which axes to substitute into `prompts/make_list.txt`, then writes a JSONL file into `wikis/<wiki>/catalogue/`. `update_index.sh` rebuilds the catalogue's `index.json` so the frontend picks up new files.

## Add a new wiki

1. `mkdir -p wikis/<name>/{catalogue,pages,prompts,frontend}`
2. Create `wikis/<name>/wiki.json` (see `wikis/data_atlas/wiki.json` for shape)
3. Create `wikis/<name>/axis.json` with your axes
4. Write `wikis/<name>/prompts/make_list.txt` using `{axis_id}` placeholders matching your axis ids
5. Copy a frontend: `cp wikis/data_atlas/frontend/* wikis/<name>/frontend/`
6. Seed empty indexes: `echo '[]' > wikis/<name>/catalogue/index.json && echo '[]' > wikis/<name>/pages/index.json`
