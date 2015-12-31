###Create journey view

Firstly upload all the images to `static/images/journeys/`

Then create a `<journeyname>.json` file in the `data/` folder.

This data file contains all the metadata about the journey and the image order.

A basic datafile with no images will look something linke this

```
{
  "service": "1. Booking",
  "last_updated": "10th Nov 2015",
  "userjourneys": []
}
```

**userjourneys** can contain multiple journeys which is useful when iterating.

Each `userjourneys` consists of

```
{
    "title": "Book a course - current site",
    "path": [{
      "caption": "Sign in",
      "imgref": "1.current.login.png",
      "note":["some note", "another note"]
    },
    ...
    ]
}
```
With each `path` entry consisting of

* A **caption**
* An **imgref**, which should be the name of the image file
* A (optional) set of **notes**, which are only visible in the zoomed in view of an image

Take a look at the [csl data file](../data/csl.json)