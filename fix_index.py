import sys

with open('e:/project/poetry-analyzer-app/templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = lines[:61] + ['''        <div class=\"hero-panel scroll-reveal\">
            <div class=\"hero-panel-card feature-card bg-subtle\" style=\"padding: 2rem;\">
                <div class=\"feature-icon-box icon-box-primary mb-4\" style=\"background: var(--color-primary-100); color: var(--color-primary); padding: 1rem; border-radius: 0.75rem; display: inline-flex; align-items: center; justify-content: center;\">
                    <svg class=\"icon\" aria-hidden=\"true\" style=\"width: 2rem; height: 2rem;\">
                        <use href=\"#icon-layer-group\"></use>
                    </svg>
                </div>
                <h3 class=\"text-xl font-bold mb-2\">100% Authentic Analysis</h3>
                <p class=\"text-sm text-soft leading-relaxed\">
                    Powered by transformer models, Stanza NLP, and strict deterministic algorithms.
                    Every score and detail is derived live from text without placeholders or mock outputs.
                </p>
            </div>
'''] + lines[92:]

with open('e:/project/poetry-analyzer-app/templates/index.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('Success')
