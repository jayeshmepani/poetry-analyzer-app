/**
 * CustomTable - A zero-dependency, declarative data table component.
 *
 * Usage in HTML:
 *
 * <table
 *   data-table
 *   data-url="/admin/users/data"
 *   data-sort="created_at"
 *   data-order="desc"
 *   data-page-size="10"
 *   data-page-list="[10,25,50,100]"
 *   data-search="true"
 *   data-click-to-select="true"
 *   data-toolbar="#toolbar"
 * >
 *   <thead>
 *     <tr>
 *       <th data-field="state" data-checkbox="true"></th>
 *       <th data-field="id"         data-sortable="true">ID</th>
 *       <th data-field="name"       data-sortable="true">Name</th>
 *       <th data-field="status"     data-formatter="statusFormatter">Status</th>
 *       <th data-field="actions"    data-formatter="actionsFormatter" data-events="actionEvents">Actions</th>
 *     </tr>
 *   </thead>
 * </table>
 *
 * Formatters are plain global functions: function statusFormatter(value, row) { return `<span>...</span>`; }
 * Events are plain global objects:
 *   window.actionEvents = {
 *     'click .edit-btn': function(e, row) { ... }
 *   }
 */

class CustomTable {
    constructor(tableEl, options = {}) {
        this.table = tableEl;
        this.opts = {
            url: tableEl.dataset.url || options.url || null,
            sort: tableEl.dataset.sort || options.sort || 'id',
            order: tableEl.dataset.order || options.order || 'asc',
            pageSize: parseInt(tableEl.dataset.pageSize || options.pageSize || 10),
            pageList: JSON.parse(tableEl.dataset.pageList || options.pageList || '[10,25,50,100]'),
            search: tableEl.dataset.search === 'true',
            clickToSelect: tableEl.dataset.clickToSelect === 'true',
            toolbar: tableEl.dataset.toolbar || options.toolbar || null,
        };

        this.state = {
            offset: 0,
            limit: this.opts.pageSize,
            sort: this.opts.sort,
            order: this.opts.order,
            search: '',
            filters: JSON.parse(tableEl.dataset.filters || '{}'), // extra server-side filters
            total: 0,
            rows: [],         // last fetched rows (for event handlers)
            selectedRows: new Set(), // stores row.id values (strings = UUID safe)
        };

        this.columns = [];
        this._parseColumns();
        this._build();
        this._refresh();
    }

    // ------------------------------------
    // 1. Parse <thead> column definitions
    // ------------------------------------
    _parseColumns() {
        const ths = this.table.querySelectorAll('thead th');
        ths.forEach(th => {
            this.columns.push({
                field: th.dataset.field || '',
                label: th.textContent.trim(),
                sortable: th.dataset.sortable === 'true',
                checkbox: th.dataset.checkbox === 'true',
                formatter: th.dataset.formatter || null,
                events: th.dataset.events || null,
                width: th.dataset.width || null,
                visible: th.dataset.visible !== 'false',
            });
        });
    }

    // ------------------------------------
    // 2. Build static wrapper DOM
    // ------------------------------------
    _build() {
        // Wrap table in a container
        const wrapper = document.createElement('div');
        wrapper.className = 'ct-wrapper';
        this.table.parentNode.insertBefore(wrapper, this.table);

        // Top bar (toolbar + search)
        const topBar = document.createElement('div');
        topBar.className = 'ct-topbar';

        // Toolbar slot
        this._toolbarSlot = document.createElement('div');
        this._toolbarSlot.className = 'ct-toolbar-slot';
        if (this.opts.toolbar) {
            const toolbarEl = document.querySelector(this.opts.toolbar);
            if (toolbarEl) this._toolbarSlot.appendChild(toolbarEl);
        }
        topBar.appendChild(this._toolbarSlot);

        // Search
        if (this.opts.search) {
            const searchWrap = document.createElement('div');
            searchWrap.className = 'ct-search';
            searchWrap.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
                </svg>
                <input type="text" class="ct-search-input" placeholder="Search...">
            `;
            topBar.appendChild(searchWrap);
        }

        wrapper.appendChild(topBar);

        // Table itself
        this.table.className = 'ct-table';
        wrapper.appendChild(this.table);

        // Build thead with sort icons
        this._buildHead();

        // Tbody placeholder
        this._tbody = this.table.querySelector('tbody');
        if (!this._tbody) {
            this._tbody = document.createElement('tbody');
            this.table.appendChild(this._tbody);
        }

        // Bottom bar (info + pagination)
        const bottomBar = document.createElement('div');
        bottomBar.className = 'ct-bottombar';
        bottomBar.innerHTML = `
            <div class="ct-info">Showing <strong class="ct-start">-</strong> to <strong class="ct-end">-</strong> of <strong class="ct-total">-</strong></div>
            <div class="ct-pagination-wrap">
                <label class="ct-per-page">
                    Per page:
                    <select class="ct-limit-select">
                        ${this.opts.pageList.map(n => `<option value="${n}" ${n === this.opts.pageSize ? 'selected' : ''}>${n}</option>`).join('')}
                    </select>
                </label>
                <div class="ct-pages"></div>
            </div>
        `;
        wrapper.appendChild(bottomBar);

        this._wrapper = wrapper;
        this._bottomBar = bottomBar;

        // Event bindings
        this._bindEvents();
    }

    _buildHead() {
        const thead = this.table.querySelector('thead');
        if (!thead) return;
        const tr = thead.querySelector('tr') || document.createElement('tr');
        thead.innerHTML = '';
        tr.innerHTML = '';

        this.columns.forEach(col => {
            if (!col.visible) return;
            const th = document.createElement('th');
            if (col.width) th.style.width = col.width + 'px';

            if (col.checkbox) {
                th.innerHTML = `<input type="checkbox" class="ct-select-all">`;
            } else if (col.sortable) {
                th.dataset.sortField = col.field;
                th.className = 'ct-sortable';
                const arrow = this.state.sort === col.field
                    ? (this.state.order === 'asc' ? '↑' : '↓')
                    : '↕';
                const arrowClass = this.state.sort === col.field ? 'ct-sort-arrow active' : 'ct-sort-arrow';
                th.innerHTML = `${col.label} <span class="${arrowClass}">${arrow}</span>`;
            } else {
                th.textContent = col.label;
            }
            tr.appendChild(th);
        });
        thead.appendChild(tr);
    }

    // ------------------------------------
    // 3. Event wiring
    // ------------------------------------
    _bindEvents() {
        // Sort
        this.table.querySelectorAll('th.ct-sortable').forEach(th => {
            th.addEventListener('click', () => {
                const field = th.dataset.sortField;
                if (this.state.sort === field) {
                    this.state.order = this.state.order === 'asc' ? 'desc' : 'asc';
                } else {
                    this.state.sort = field;
                    this.state.order = 'asc';
                }
                this.state.offset = 0;
                this._buildHead();
                this._bindEvents();
                this._refresh();
            });
        });

        // Select all
        const selectAll = this.table.querySelector('.ct-select-all');
        if (selectAll) {
            selectAll.addEventListener('change', e => {
                this.state.selectedRows.clear();
                this._tbody.querySelectorAll('.ct-row-check:not(:disabled)').forEach(cb => {
                    cb.checked = e.target.checked;
                    if (e.target.checked) this.state.selectedRows.add(parseInt(cb.value));
                });
                this._emitSelectionChange();
            });
        }

        // Search
        if (this.opts.search) {
            const input = this._wrapper.querySelector('.ct-search-input');
            if (input) {
                let timer;
                input.addEventListener('input', () => {
                    clearTimeout(timer);
                    timer = setTimeout(() => {
                        this.state.search = input.value.trim();
                        this.state.offset = 0;
                        this._refresh();
                    }, 350);
                });
            }
        }

        // Limit
        const limitSel = this._bottomBar.querySelector('.ct-limit-select');
        if (limitSel) {
            limitSel.addEventListener('change', () => {
                this.state.limit = parseInt(limitSel.value);
                this.state.offset = 0;
                this._refresh();
            });
        }
    }

    // ------------------------------------
    // 4. Fetch + render
    // ------------------------------------
    async _refresh() {
        if (!this.opts.url) return;
        this._setLoading(true);

        try {
            // ── All params sent to server — nothing filtered client-side ──
            const params = new URLSearchParams({
                limit: this.state.limit,
                offset: this.state.offset,
                sort: this.state.sort,
                order: this.state.order,
                search: this.state.search,
            });

            // Append any active filters as individual query params
            Object.entries(this.state.filters).forEach(([k, v]) => {
                if (v !== '' && v !== null && v !== undefined) params.set(k, v);
            });

            const res = await axios.get(`${this.opts.url}?${params}`);
            const data = res.data?.data ?? res.data; // handle {success, data} or plain {total, rows}
            this.state.total = data.total || 0;
            this.state.rows = data.rows || [];
            this._renderRows(this.state.rows);
            this._renderPagination();
            this._updateInfo();
        } catch (err) {
            this._tbody.innerHTML = `<tr><td colspan="${this.columns.length}" class="ct-msg ct-error">Failed to load data</td></tr>`;
        } finally {
            this._setLoading(false);
        }
    }

    _renderRows(rows) {
        if (!rows.length) {
            this._tbody.innerHTML = `<tr><td colspan="${this.columns.length}" class="ct-msg">No records found</td></tr>`;
            return;
        }

        // row.id is used as the row identifier — works with integers AND uuid strings
        this._tbody.innerHTML = rows.map(row => {
            const rowId = String(row.id); // UUID-safe string key
            const tds = this.columns
                .filter(col => col.visible)
                .map(col => {
                    if (col.checkbox) {
                        return `<td><input type="checkbox" class="ct-row-check" value="${rowId}" ${this.state.selectedRows.has(rowId) ? 'checked' : ''}></td>`;
                    }
                    let value = row[col.field] ?? '';
                    if (col.formatter && typeof window[col.formatter] === 'function') {
                        value = window[col.formatter](value, row);
                    }
                    return `<td>${value}</td>`;
                }).join('');
            return `<tr data-id="${rowId}">${tds}</tr>`;
        }).join('');

        // Bind row checkboxes — store as UUID strings
        this._tbody.querySelectorAll('.ct-row-check').forEach(cb => {
            cb.addEventListener('change', () => {
                const id = cb.value; // string (UUID safe)
                if (cb.checked) this.state.selectedRows.add(id);
                else this.state.selectedRows.delete(id);
                this._emitSelectionChange();
            });
        });

        // Click-to-select rows
        if (this.opts.clickToSelect) {
            this._tbody.querySelectorAll('tr').forEach(tr => {
                tr.addEventListener('click', (e) => {
                    if (e.target.tagName === 'INPUT' || e.target.tagName === 'BUTTON' || e.target.closest('button')) return;
                    const cb = tr.querySelector('.ct-row-check');
                    if (cb && !cb.disabled) {
                        cb.checked = !cb.checked;
                        cb.dispatchEvent(new Event('change'));
                    }
                });
            });
        }

        // Bind custom column events — pass the full row object from last fetch
        this.columns.filter(c => c.events).forEach(col => {
            const eventsObj = window[col.events];
            if (!eventsObj) return;
            Object.entries(eventsObj).forEach(([eventSelector, handler]) => {
                const [eventName, ...selParts] = eventSelector.split(' ');
                const selector = selParts.join(' ');
                this._tbody.querySelectorAll(selector).forEach(el => {
                    el.addEventListener(eventName, (e) => {
                        const tr = e.target.closest('tr');
                        const rowId = tr?.dataset.id;
                        const rowData = this.state.rows.find(r => String(r.id) === rowId);
                        handler(e, rowData);
                    });
                });
            });
        });
    }

    // ------------------------------------
    // 5. Pagination
    // ------------------------------------
    _renderPagination() {
        const pages = this._bottomBar.querySelector('.ct-pages');
        const total = this.state.total;
        const limit = this.state.limit;
        const offset = this.state.offset;
        const current = Math.floor(offset / limit);
        const totalPages = Math.ceil(total / limit);

        const pageNums = this._pagesToShow(current, totalPages);
        pages.innerHTML = '';

        const mk = (label, disabled, active, action) => {
            const btn = document.createElement('button');
            btn.className = `ct-page-btn${active ? ' active' : ''}`;
            btn.disabled = disabled;
            btn.innerHTML = label;
            btn.addEventListener('click', action);
            pages.appendChild(btn);
        };

        mk('&laquo;', current === 0, false, () => { this.state.offset = 0; this._refresh(); });
        mk('&lsaquo;', current === 0, false, () => { this.state.offset = Math.max(0, offset - limit); this._refresh(); });

        pageNums.forEach(p => {
            if (p === '...') {
                const sp = document.createElement('span');
                sp.className = 'ct-page-ellipsis';
                sp.textContent = '…';
                pages.appendChild(sp);
            } else {
                mk(p + 1, false, p === current, () => { this.state.offset = p * limit; this._refresh(); });
            }
        });

        mk('&rsaquo;', current >= totalPages - 1, false, () => { this.state.offset = Math.min((totalPages - 1) * limit, offset + limit); this._refresh(); });
        mk('&raquo;', current >= totalPages - 1, false, () => { this.state.offset = (totalPages - 1) * limit; this._refresh(); });
    }

    _pagesToShow(current, total) {
        if (total <= 7) return Array.from({ length: total }, (_, i) => i);
        const pages = [];
        if (current <= 3) {
            for (let i = 0; i < 5; i++) pages.push(i);
            pages.push('...'); pages.push(total - 1);
        } else if (current >= total - 4) {
            pages.push(0); pages.push('...');
            for (let i = total - 5; i < total; i++) pages.push(i);
        } else {
            pages.push(0); pages.push('...');
            for (let i = current - 1; i <= current + 1; i++) pages.push(i);
            pages.push('...'); pages.push(total - 1);
        }
        return pages;
    }

    _updateInfo() {
        const start = this.state.total === 0 ? 0 : this.state.offset + 1;
        const end = Math.min(this.state.offset + this.state.limit, this.state.total);
        this._bottomBar.querySelector('.ct-start').textContent = start;
        this._bottomBar.querySelector('.ct-end').textContent = end;
        this._bottomBar.querySelector('.ct-total').textContent = this.state.total;
    }

    _setLoading(on) {
        if (on) {
            this._tbody.innerHTML = `<tr><td colspan="${this.columns.length}" class="ct-msg ct-loading"><span class="ct-spinner"></span> Loading...</td></tr>`;
        }
    }

    // ------------------------------------
    // 6. Public API
    // ------------------------------------
    refresh() { this.state.offset = 0; this._refresh(); }
    refreshCurrent() { this._refresh(); }   // refresh without resetting page
    getSelections() { return [...this.state.selectedRows]; }  // returns UUID strings
    clearSelections() { this.state.selectedRows.clear(); this._emitSelectionChange(); }

    // Server-side filters — each call appends a param to every request
    setFilter(key, value) {
        this.state.filters[key] = value;
        this.state.offset = 0;
        this._refresh();
    }
    clearFilters() {
        this.state.filters = {};
        this.state.offset = 0;
        this._refresh();
    }

    _emitSelectionChange() {
        this.table.dispatchEvent(new CustomEvent('ct:selectionChange', { detail: [...this.state.selectedRows] }));
    }
}

// ------------------------------------
// Auto-init all [data-table] elements
// ------------------------------------
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-table]').forEach(el => {
        el._customTable = new CustomTable(el);
    });
});

// Helper to get instance
window.getTable = (selector) => {
    const el = typeof selector === 'string' ? document.querySelector(selector) : selector;
    return el?._customTable || null;
};
