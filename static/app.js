/**
 * app.js - Lógica del lado del cliente para la Lista de Compras Familiar
 */

document.addEventListener('DOMContentLoaded', () => {
    // Selectores para Lista
    const itemsContainer = document.getElementById('items-container');
    const filterCategory = document.getElementById('filter-category');
    const filterStatus = document.getElementById('filter-status');
    const searchQ = document.getElementById('search-q');

    // Selectores para Agregar Item
    const addItemForm = document.getElementById('add-item-form');
    const itemCategorySelect = document.getElementById('category');
    const storeSelect = document.getElementById('store-select');
    const btnApplyTemplate = document.getElementById('btn-apply-template');

    // Selectores para Categorías
    const addCategoryForm = document.getElementById('add-category-form');
    const categoriesList = document.getElementById('categories-list');

    // Selectores para Estadísticas
    const statsTotal = document.getElementById('stat-total');
    const statsPending = document.getElementById('stat-pending');
    const statsDone = document.getElementById('stat-done');
    const categoryStatsBody = document.getElementById('category-stats-body');

    // Selector de error común
    const errorContainer = document.getElementById('error-message') || document.getElementById('message');

    // --- LÓGICA DE LA PANTALLA DE LISTA ---
    if (itemsContainer) {
        loadCategories(filterCategory);
        loadItems();
        filterCategory.addEventListener('change', loadItems);
        filterStatus.addEventListener('change', loadItems);
        let debounceTimer;
        searchQ.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(loadItems, 300);
        });
    }

    // --- LÓGICA DE LA PANTALLA DE AGREGAR ITEM ---
    if (addItemForm) {
        loadCategories(itemCategorySelect);
        loadTemplatesForSelect(storeSelect);

        addItemForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                name: document.getElementById('name').value,
                qty: document.getElementById('qty').value,
                category: document.getElementById('category').value
            };
            try {
                await apiFetch('/api/items', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                window.location.href = '/';
            } catch (err) {
                showError(err.message);
            }
        });

        if (btnApplyTemplate) {
            btnApplyTemplate.addEventListener('click', async () => {
                const store = storeSelect.value;
                if (!store) return showError('Seleccione una tienda');
                try {
                    await apiFetch('/api/templates/apply', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ store })
                    });
                    window.location.href = '/';
                } catch (err) {
                    showError(err.message);
                }
            });
        }
    }

    // --- LÓGICA DE LA PANTALLA DE CATEGORÍAS ---
    if (categoriesList) {
        renderCategories();
        if (addCategoryForm) {
            addCategoryForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const name = document.getElementById('category-name').value;
                try {
                    await apiFetch('/api/categories', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ name })
                    });
                    document.getElementById('category-name').value = '';
                    renderCategories();
                } catch (err) {
                    showError(err.message);
                }
            });
        }
    }

    // --- LÓGICA DE LA PANTALLA DE ESTADÍSTICAS ---
    if (statsTotal) {
        loadStats();
    }

    /**
     * Carga las tiendas disponibles en el selector de plantillas
     */
    async function loadTemplatesForSelect(selectElement) {
        if (!selectElement) return;
        try {
            const data = await apiFetch('/api/templates');
            Object.keys(data.stores).forEach(store => {
                const option = document.createElement('option');
                option.value = store;
                option.textContent = store;
                selectElement.appendChild(option);
            });
        } catch (err) {
            console.error('Error al cargar plantillas:', err);
        }
    }

    /**
     * Carga y renderiza las estadísticas
     */
    async function loadStats() {
        try {
            const stats = await apiFetch('/api/stats');
            statsTotal.textContent = stats.total_items;
            statsPending.textContent = stats.total_pending;
            statsDone.textContent = stats.total_done;

            if (categoryStatsBody) {
                categoryStatsBody.innerHTML = '';
                stats.by_category.forEach(row => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${row.category}</td>
                        <td>${row.total}</td>
                        <td>${row.done}</td>
                        <td>${row.pending}</td>
                    `;
                    categoryStatsBody.appendChild(tr);
                });
            }
        } catch (err) {
            showError('Error al cargar estadísticas');
        }
    }

    /**
     * Carga las categorías en un elemento select
     */
    async function loadCategories(selectElement) {
        if (!selectElement) return;
        try {
            const categories = await apiFetch('/api/categories');
            const firstOption = selectElement.options[0];
            selectElement.innerHTML = '';
            selectElement.appendChild(firstOption);

            categories.forEach(cat => {
                if (cat !== 'Sin categoría') {
                    const option = document.createElement('option');
                    option.value = cat;
                    option.textContent = cat;
                    selectElement.appendChild(option);
                }
            });
        } catch (err) {
            showError('Error al cargar categorías');
        }
    }

    /**
     * Renderiza la lista de categorías con botón de borrar
     */
    async function renderCategories() {
        if (!categoriesList) return;
        try {
            const categories = await apiFetch('/api/categories');
            categoriesList.innerHTML = '';
            categories.forEach(cat => {
                const li = document.createElement('li');
                li.className = 'item-row';
                li.innerHTML = `
                    <span class="item-name">${cat}</span>
                    ${cat !== 'Sin categoría' ? `<button class="btn-danger btn-delete-cat" data-name="${cat}" title="Eliminar"><i class="fas fa-trash-alt"></i></button>` : ''}
                `;
                categoriesList.appendChild(li);
            });

            document.querySelectorAll('.btn-delete-cat').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const target = e.currentTarget;
                    deleteCategory(target.dataset.name);
                });
            });
        } catch (err) {
            showError('Error al cargar categorías');
        }
    }

    async function deleteCategory(name) {
        if (!confirm(`¿Borrar la categoría "${name}"?`)) return;
        try {
            await apiFetch(`/api/categories/${name}`, { method: 'DELETE' });
            renderCategories();
        } catch (err) {
            showError(err.message);
        }
    }

    async function loadItems() {
        showError(null);
        const params = new URLSearchParams();
        if (filterCategory.value) params.append('category', filterCategory.value);
        if (filterStatus.value) params.append('done', filterStatus.value);
        if (searchQ.value) params.append('q', searchQ.value);

        try {
            const items = await apiFetch(`/api/items?${params.toString()}`);
            renderItems(items);
        } catch (err) {
            showError('Error al cargar la lista');
        }
    }

    function renderItems(items) {
        itemsContainer.innerHTML = items.length ? '' : '<div class="card text-center"><p>No hay items en la lista.</p></div>';
        items.forEach(item => {
            const row = document.createElement('div');
            row.className = `item-row ${item.done ? 'done' : ''}`;
            row.innerHTML = `
                <input type="checkbox" ${item.done ? 'checked' : ''} data-id="${item.id}" class="toggle-done" aria-label="Marcar como comprado">
                <div class="item-name">${item.name} <span class="item-meta"><i class="fas fa-tag"></i> ${item.qty}</span></div>
                <div class="badge badge-category">${item.category}</div>
                <button class="btn-danger btn-delete" data-id="${item.id}" title="Eliminar"><i class="fas fa-trash-alt"></i></button>
            `;
            itemsContainer.appendChild(row);
        });

        document.querySelectorAll('.toggle-done').forEach(cb => {
            cb.addEventListener('change', (e) => toggleItem(e.target.dataset.id, e.target.checked));
        });
        document.querySelectorAll('.btn-delete').forEach(btn => {
            btn.addEventListener('click', (e) => deleteItem(e.target.dataset.id));
        });
    }

    async function toggleItem(id, done) {
        try {
            await apiFetch(`/api/items/${id}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ done })
            });
            loadItems();
        } catch (err) {
            showError('Error al actualizar');
        }
    }

    async function deleteItem(id) {
        if (!confirm('¿Eliminar item?')) return;
        try {
            await apiFetch(`/api/items/${id}`, { method: 'DELETE' });
            loadItems();
        } catch (err) {
            showError('Error al eliminar');
        }
    }

    function showError(msg) {
        if (!errorContainer) return;
        errorContainer.textContent = msg || '';
        errorContainer.style.display = msg ? 'block' : 'none';
        if (msg) errorContainer.style.background = '#fee';
    }
});

async function apiFetch(endpoint, options = {}) {
    const response = await fetch(endpoint, options);
    if (response.status === 204) return null;
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Error en la petición');
    return data;
}
