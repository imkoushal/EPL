# Tutorial 5: Building a static routing Blog Engine

Let's look at one final capability inside the EPL Web Framework: complex, explicit frontend page rendering routing.

Instead of generic API endpoints, we can map URLs directly to visually rendered standard Web Interface pages.

## Creating the Layout Tree

EPL uses indentation (just like standard code) to formulate a strict DOM tree!

```epl
Create WebApp called blogApp

Route "/post/hello-epl" shows
    Page "Hello EPL"
        Heading "Hello EPL - The Future of Code"
        SubHeading "Published: March 2026"
        
        Text "Welcome to my new blog! This blog isn't powered by WordPress or Next.js."
        Text "It is actually powered natively by the English Programming Language."
        
        Link "← Back to Home" to "/"
    End
End

Start blogApp on port 4000
```

By defining explicit sub-pages, the EPL web framework natively converts your blocks directly into minified, high-performance HTML markup. 

It handles `<meta>` tags, headers, layout spacing, CSS inclusion, typography normalization, and viewport setup completely implicitly!
