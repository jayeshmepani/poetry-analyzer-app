with open("static/css/app.css", "r", encoding="utf-8") as f:
    content = f.read()

target = """        --destructive-foreground: var(--ink-950);

        --ring: var(--royal-purple-500);
    }
        font-size: var(--text-base);
    }"""

repl = """        --destructive-foreground: var(--ink-950);

        --ring: var(--royal-purple-500);
    }

    /* Compatibility Mappings */
    :root {
        --color-bg: var(--background);
        --color-surface: var(--card);
        --color-border: var(--border);
        --color-border-strong: color-mix(in oklch, var(--border) 70%, var(--foreground));
        --color-text: var(--foreground);
        --color-text-soft: var(--muted-foreground);
        --color-text-muted: color-mix(in oklch, var(--muted-foreground) 70%, var(--background));
        --color-bg-subtle: var(--muted);
        
        --color-primary: var(--primary);
        --color-primary-hover: color-mix(in oklch, var(--primary) 85%, var(--foreground));
        --color-primary-active: color-mix(in oklch, var(--primary) 70%, var(--foreground));
        --color-primary-border: color-mix(in oklch, var(--primary) 30%, transparent);
        --color-primary-subtle: color-mix(in oklch, var(--primary) 15%, transparent);

        --color-secondary: var(--secondary);
        --color-secondary-hover: color-mix(in oklch, var(--secondary) 85%, var(--foreground));
        --color-secondary-border: color-mix(in oklch, var(--secondary) 30%, transparent);
        --color-secondary-subtle: color-mix(in oklch, var(--secondary) 15%, transparent);

        --color-accent: var(--accent);
        --color-accent-border: color-mix(in oklch, var(--accent) 30%, transparent);
        --color-accent-subtle: color-mix(in oklch, var(--accent) 15%, transparent);

        --color-success: var(--prim-success, var(--royal-emerald-600));
        --color-success-text: color-mix(in oklch, var(--color-success) 80%, var(--foreground));
        --color-success-border: color-mix(in oklch, var(--color-success) 30%, transparent);
        --color-success-subtle: color-mix(in oklch, var(--color-success) 15%, transparent);

        --color-danger: var(--destructive, var(--crimson-600));
        --color-danger-text: color-mix(in oklch, var(--color-danger) 80%, var(--foreground));
        --color-danger-border: color-mix(in oklch, var(--color-danger) 30%, transparent);
        --color-danger-subtle: color-mix(in oklch, var(--color-danger) 15%, transparent);

        --color-warning: var(--prim-warning, oklch(75% 0.17 86));
        --color-warning-text: color-mix(in oklch, var(--color-warning) 80%, var(--foreground));
        --color-warning-border: color-mix(in oklch, var(--color-warning) 30%, transparent);
        --color-warning-subtle: color-mix(in oklch, var(--color-warning) 15%, transparent);

        --color-info: var(--info, var(--royal-teal-500));
        --color-info-text: color-mix(in oklch, var(--color-info) 80%, var(--foreground));
        --color-info-border: color-mix(in oklch, var(--color-info) 30%, transparent);
        --color-info-subtle: color-mix(in oklch, var(--color-info) 15%, transparent);
        
        --color-focus-ring: var(--ring);
    }
}

@layer base {
    body {
        font-family: var(--font-sans);
        font-size: var(--text-base);
        line-height: var(--leading-normal);
        background: var(--color-bg);
        color: var(--color-text);
        min-height: 100dvh;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    /* Heading scale */
    h1 {
        font-size: var(--text-xl);
        letter-spacing: var(--tracking-tight);
    }

    h2 {
        font-size: var(--text-lg);
        letter-spacing: var(--tracking-tight);
    }

    h3 {
        font-size: var(--text-md);
    }

    h4 {
        font-size: var(--text-base);
    }"""

if target in content:
    new_content = content.replace(target, repl)
    with open("static/css/app.css", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Successfully replaced.")
else:
    print("Target not found.")
