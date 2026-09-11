#!/usr/bin/env julia
#
# make_thumb.jl - give a recipe the thumbnail that shows on its gallery card.
#
# The picture work is `Mera.makethumb`; this only knows about the gallery's layout, so it can
# find your recipe's media/ and name the output after your notebook.
#
# Every recipe shows a thumbnail on the gallery page, and the grid only looks like a grid if
# they all share one size. Gallery notebooks are stored without outputs, so the picture has to
# come from a file your notebook wrote: a saved figure, or the preview gif.
#
# Usage, from the gallery folder:
#
#     julia make_thumb.jl 001_coin_flip_movie
#         Look in that recipe's media/ for something to use.
#
#     julia make_thumb.jl coin_flip_movie
#         The number is optional as long as the rest is unambiguous.
#
#     julia make_thumb.jl 001_coin_flip_movie --from 001_coin_flip_movie/media/preview.gif
#         Use a particular file, when the folder holds several.
#
#     julia make_thumb.jl 001_coin_flip_movie --frame 0.25
#         For a gif, take the frame a quarter of the way in. The default is 0.4, because an
#         animation that opens on a static pose makes a dull thumbnail from frame 0.
#
#     julia make_thumb.jl 001_coin_flip_movie --crop [top|bottom|left|right]
#         Fill the card instead of fitting the picture into it. By default the whole picture is
#         kept and the spare space padded with its own background colour, because cropping a
#         wide multi-panel figure cuts off its outer panels.
#
# A movie is not read: save a frame from the code that made it, or point this at the preview
# gif. There is nothing to install. The script runs in your recipe's own environment, which
# already has Mera.
#
# Set MERA_DIR to a Mera.jl checkout and the thumbnail is copied into docs/src/assets/gallery
# as well, so the documentation page picks it up with no extra step.

using Pkg

const GALLERY = @__DIR__
const WIDTH, HEIGHT = 800, 450
const SIZE_BUDGET = 250_000

fail(msg) = (println(stderr, msg); exit(1))

"A recipe is a folder holding a notebook. Accept its name, its number, or the notebook's name."
function resolve_recipe_dir(gallery, name)
    name = rstrip(name, '/')
    endswith(name, ".ipynb") && (name = name[1:end-6])
    isdir(joinpath(gallery, name)) && !isempty(filter(endswith(".ipynb"),
        readdir(joinpath(gallery, name)))) && return joinpath(gallery, name)

    isrecipe = d -> isdir(joinpath(gallery, d)) && !startswith(d, '.') &&
                    any(endswith(".ipynb"), readdir(joinpath(gallery, d)))
    dirs = filter(isrecipe, readdir(gallery))
    hits = filter(d -> d == name || startswith(d, name * "_") ||
                       last(split(d, '_', limit = 2)) == name, dirs)
    length(hits) == 1 && return joinpath(gallery, only(hits))
    length(hits) > 1 && fail("'$name' matches several recipes: $(join(hits, ", "))")
    fail("""
         No recipe folder for '$name'. This gallery has: $(join(dirs, ", "))
         Each recipe lives in its own numbered folder, e.g. 002_$name/ holding the notebook,
         its Project.toml and its media/.""")
end

"The thumbnail is named after the notebook, so the card and the notebook agree."
function notebook_name(recipe_dir)
    books = filter(endswith(".ipynb"), readdir(recipe_dir))
    isempty(books) ? basename(recipe_dir) : first(books)[1:end-6]
end

"What the recipe produced, preferring a still over an animation."
function discover(recipe, media_dir)
    isdir(media_dir) || return String[]
    usable = f -> begin
        e = lowercase(splitext(f)[2])
        !endswith(f, "_thumb.png") && e in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".tif") &&
            (occursin(recipe, f) || occursin(splitext(f)[1], recipe))
    end
    hits = filter(usable, readdir(media_dir))
    joinpath.(media_dir, sort(hits; by = f -> (lowercase(splitext(f)[2]) == ".gif", f)))
end

function parse_args(argv)
    isempty(argv) && fail("Usage: julia make_thumb.jl <recipe-folder> [--from FILE] " *
                          "[--frame 0.0-1.0] [--crop [top|bottom|left|right]]")
    recipe, source, frame, mode, anchor = argv[1], nothing, 0.4, :fit, :center
    i = 2
    while i <= length(argv)
        a = argv[i]
        if a == "--from"
            i += 1; i > length(argv) && fail("--from needs a file")
            source = argv[i]
        elseif a == "--frame"
            i += 1; i > length(argv) && fail("--frame needs a number")
            v = tryparse(Float64, argv[i])
            v === nothing && fail("--frame takes a number from 0.0 to 1.0")
            frame = v
        elseif a == "--crop"
            mode = :crop
            if i < length(argv) && argv[i+1] in ("top", "bottom", "left", "right", "center")
                i += 1; anchor = Symbol(argv[i])
            end
        else
            fail("Unknown option: $a")
        end
        i += 1
    end
    0.0 <= frame <= 1.0 || fail("--frame is a position from 0.0 to 1.0, not a frame number.")
    return (; recipe, source, frame, mode, anchor)
end

const ARGS_PARSED = parse_args(ARGS)
const RECIPE_DIR = resolve_recipe_dir(GALLERY, ARGS_PARSED.recipe)

# Run in the recipe's own environment: it already pins Mera, which is where the picture work
# lives, so there is nothing extra for a contributor to install.
Pkg.activate(RECIPE_DIR; io = devnull)
try
    Pkg.instantiate(; io = devnull)
catch
    fail("Could not set up $(basename(RECIPE_DIR))'s environment. Run the notebook once first, " *
         "or check its Project.toml.")
end

using Mera

function main()
    recipe = notebook_name(RECIPE_DIR)
    media = joinpath(RECIPE_DIR, "media")

    src = if ARGS_PARSED.source !== nothing
        p = isabspath(ARGS_PARSED.source) ? ARGS_PARSED.source :
            isfile(joinpath(pwd(), ARGS_PARSED.source)) ? joinpath(pwd(), ARGS_PARSED.source) :
            joinpath(GALLERY, ARGS_PARSED.source)
        isfile(p) || fail("No such file: $(ARGS_PARSED.source)")
        p
    else
        found = discover(recipe, media)
        isempty(found) && fail("""
            Nothing in $(basename(RECIPE_DIR))/media/ looks like a picture for '$recipe'.
            Save a figure from your notebook and pass it with --from, e.g.
                julia make_thumb.jl $(basename(RECIPE_DIR)) --from $(basename(RECIPE_DIR))/media/$recipe.png
            A movie cannot be used directly: save a frame, or use the preview gif.""")
        length(found) > 1 && println("candidates: ", join(basename.(found), ", "))
        println("using ", basename(first(found)))
        first(found)
    end

    out = joinpath(media, "$(recipe)_thumb.png")
    try
        makethumb(src, out; width = WIDTH, height = HEIGHT,
                  mode = ARGS_PARSED.mode, anchor = ARGS_PARSED.anchor, frame = ARGS_PARSED.frame)
    catch e
        e isa ArgumentError ? fail(e.msg) : rethrow()
    end

    bytes = filesize(out)
    how = ARGS_PARSED.mode === :fit ? "fitted whole" : "cropped to $(ARGS_PARSED.anchor)"
    println("wrote $(relpath(out, GALLERY))  $(WIDTH)x$(HEIGHT) ($how), $(bytes ÷ 1000) kB")
    bytes > SIZE_BUDGET && println("  that is over the $(SIZE_BUDGET ÷ 1000) kB budget a card " *
                                   "page should keep to. A larger, flatter source compresses better.")

    mera = get(ENV, "MERA_DIR", "")
    if isempty(mera)
        println("set MERA_DIR to a Mera.jl checkout to have it copied into the docs as well.")
    elseif isdir(joinpath(mera, "docs", "src", "assets"))
        target = joinpath(mera, "docs", "src", "assets", "gallery")
        mkpath(target)
        cp(out, joinpath(target, basename(out)); force = true)
        println("copied into ", target)
    else
        println("MERA_DIR=$mera does not look like a Mera.jl checkout; not copying.")
    end
end

main()
