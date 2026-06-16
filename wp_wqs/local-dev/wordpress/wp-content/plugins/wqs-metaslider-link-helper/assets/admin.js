(function () {
    var config = window.wqsMetaSliderLinkHelper || {};
    var strings = config.strings || {};

    function debounce(callback, delay) {
        var timer = null;

        return function () {
            var args = arguments;
            window.clearTimeout(timer);
            timer = window.setTimeout(function () {
                callback.apply(null, args);
            }, delay);
        };
    }

    function request(action, params) {
        var url = new URL(config.ajaxUrl || window.ajaxurl);
        url.searchParams.set('action', action);
        url.searchParams.set('nonce', config.nonce || '');

        Object.keys(params || {}).forEach(function (key) {
            if (params[key] !== undefined && params[key] !== null) {
                url.searchParams.set(key, params[key]);
            }
        });

        return fetch(url.toString(), { credentials: 'same-origin' })
            .then(function (response) {
                return response.json();
            })
            .then(function (payload) {
                if (!payload || !payload.success) {
                    return [];
                }

                return payload.data && payload.data.items ? payload.data.items : [];
            });
    }

    function setSelectLoading(select) {
        select.innerHTML = '';
        var option = document.createElement('option');
        option.textContent = strings.loading || 'Loading...';
        option.value = '';
        select.appendChild(option);
    }

    function renderResults(select, items, selectedId, includeAllCategories) {
        select.innerHTML = '';

        if (includeAllCategories) {
            var allOption = document.createElement('option');
            allOption.textContent = strings.allCategories || 'All categories';
            allOption.value = '';
            allOption.dataset.id = '';
            select.appendChild(allOption);
        }

        if (!items.length) {
            var emptyOption = document.createElement('option');
            emptyOption.textContent = strings.noResults || 'No results found.';
            emptyOption.value = '';
            select.appendChild(emptyOption);
            return;
        }

        items.forEach(function (item) {
            var option = document.createElement('option');
            option.value = item.target || String(item.id);
            option.textContent = item.label;
            option.dataset.id = String(item.id);
            option.dataset.label = item.label;
            option.dataset.url = item.url;

            if (selectedId && String(item.id) === String(selectedId)) {
                option.selected = true;
            }

            select.appendChild(option);
        });
    }

    function updateNativeFields(root, url, label) {
        var tabWrap = root.closest('.tabs-content');
        if (!tabWrap) {
            return;
        }

        var urlInput = tabWrap.querySelector('input.url');
        if (urlInput && url) {
            urlInput.value = url;
            urlInput.dispatchEvent(new Event('change', { bubbles: true }));
            urlInput.dispatchEvent(new Event('input', { bubbles: true }));
        }

        var altInput = tabWrap.querySelector('input[name$="[link-alt]"]');
        if (altInput && !altInput.value && label) {
            altInput.value = label.replace(/\s+\((post|page|category)\s+#\d+\)$/i, '');
            altInput.dispatchEvent(new Event('change', { bubbles: true }));
            altInput.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }

    function updateCurrentTarget(root, url, label) {
        var currentLink = root.querySelector('.wqs-ms-current-target__link');
        var currentEmpty = root.querySelector('.wqs-ms-current-target__empty');

        if (!currentLink || !currentEmpty) {
            return;
        }

        if (!url) {
            currentLink.hidden = true;
            currentLink.href = '';
            currentLink.textContent = '';
            currentEmpty.hidden = false;
            currentEmpty.textContent = strings.manualLink || 'Using the original MetaSlider link field.';
            return;
        }

        currentLink.hidden = false;
        currentLink.href = url;
        currentLink.textContent = label || url;
        currentEmpty.hidden = true;
    }

    function setTarget(root, target, url, label) {
        var targetInput = root.querySelector('.wqs-ms-link-target-value');
        if (targetInput) {
            targetInput.value = target || '';
            targetInput.dispatchEvent(new Event('change', { bubbles: true }));
        }

        updateCurrentTarget(root, url, label);

        if (target) {
            updateNativeFields(root, url, label);
        }
    }

    function getSelectedId(root, kind) {
        return root.dataset.selectedKind === kind ? root.dataset.selectedId : '';
    }

    function loadCategories(root, select, searchInput, selectedId, includeAllCategories) {
        setSelectLoading(select);

        return request('wqs_ms_link_categories', {
            search: searchInput ? searchInput.value : '',
            selected: selectedId || '',
        }).then(function (items) {
            renderResults(select, items, selectedId, includeAllCategories);
        });
    }

    function loadPosts(root) {
        var postResults = root.querySelector('.wqs-ms-post-results');
        var postSearch = root.querySelector('.wqs-ms-post-search');
        var categoryResults = root.querySelector('.wqs-ms-post-category-results');
        var selectedOption = categoryResults ? categoryResults.options[categoryResults.selectedIndex] : null;
        var categoryId = selectedOption && selectedOption.dataset ? selectedOption.dataset.id : '';

        if (!postResults) {
            return Promise.resolve();
        }

        setSelectLoading(postResults);

        return request('wqs_ms_link_posts', {
            search: postSearch ? postSearch.value : '',
            category: categoryId || '',
            selected: getSelectedId(root, 'post'),
        }).then(function (items) {
            renderResults(postResults, items, getSelectedId(root, 'post'), false);
        });
    }

    function showMode(root, mode) {
        var targetInput = root.querySelector('.wqs-ms-link-target-value');

        root.querySelectorAll('.wqs-ms-link-panel').forEach(function (panel) {
            panel.hidden = panel.dataset.panel !== mode;
        });

        if (mode === 'none') {
            setTarget(root, '', '', '');
            return;
        }

        if (mode === 'category') {
            var categorySelect = root.querySelector('.wqs-ms-category-results');
            var categorySearch = root.querySelector('.wqs-ms-category-search');
            loadCategories(root, categorySelect, categorySearch, getSelectedId(root, 'category'), false);
            return;
        }

        if (mode === 'post') {
            var postCategorySelect = root.querySelector('.wqs-ms-post-category-results');
            var postCategorySearch = root.querySelector('.wqs-ms-post-category-search');
            loadCategories(root, postCategorySelect, postCategorySearch, '', true).then(function () {
                loadPosts(root);
            });

            if (targetInput && targetInput.value.indexOf('post:') !== 0) {
                targetInput.value = '';
            }
        }
    }

    function selectedOptionData(select) {
        var option = select.options[select.selectedIndex];
        if (!option || !option.value) {
            return null;
        }

        return {
            target: option.value,
            id: option.dataset.id,
            label: option.dataset.label || option.textContent,
            url: option.dataset.url || '',
        };
    }

    function init(root) {
        if (root.dataset.wqsInitialized === '1') {
            return;
        }

        root.dataset.wqsInitialized = '1';

        var selectedUrl = root.dataset.selectedUrl || '';
        var selectedLabel = root.dataset.selectedLabel || '';
        updateCurrentTarget(root, selectedUrl, selectedLabel);

        root.querySelectorAll('input[name$="[wqs_link_mode]"]').forEach(function (radio) {
            radio.addEventListener('change', function () {
                if (radio.checked) {
                    showMode(root, radio.value);
                }
            });

            if (radio.checked) {
                showMode(root, radio.value);
            }
        });

        var categorySearch = root.querySelector('.wqs-ms-category-search');
        var categorySelect = root.querySelector('.wqs-ms-category-results');
        var reloadCategoryMode = debounce(function () {
            loadCategories(root, categorySelect, categorySearch, getSelectedId(root, 'category'), false);
        }, 250);

        if (categorySearch) {
            categorySearch.addEventListener('input', reloadCategoryMode);
        }

        if (categorySelect) {
            categorySelect.addEventListener('change', function () {
                var data = selectedOptionData(categorySelect);
                if (data) {
                    setTarget(root, data.target, data.url, data.label);
                }
            });
        }

        var postCategorySearch = root.querySelector('.wqs-ms-post-category-search');
        var postCategorySelect = root.querySelector('.wqs-ms-post-category-results');
        var reloadPostCategories = debounce(function () {
            loadCategories(root, postCategorySelect, postCategorySearch, '', true).then(function () {
                loadPosts(root);
            });
        }, 250);

        if (postCategorySearch) {
            postCategorySearch.addEventListener('input', reloadPostCategories);
        }

        if (postCategorySelect) {
            postCategorySelect.addEventListener('change', function () {
                loadPosts(root);
            });
        }

        var postSearch = root.querySelector('.wqs-ms-post-search');
        var reloadPosts = debounce(function () {
            loadPosts(root);
        }, 250);

        if (postSearch) {
            postSearch.addEventListener('input', reloadPosts);
        }

        var postSelect = root.querySelector('.wqs-ms-post-results');
        if (postSelect) {
            postSelect.addEventListener('change', function () {
                var data = selectedOptionData(postSelect);
                if (data) {
                    setTarget(root, data.target, data.url, data.label);
                }
            });
        }
    }

    function initAll(container) {
        (container || document).querySelectorAll('.wqs-ms-link-helper').forEach(init);
    }

    document.addEventListener('DOMContentLoaded', function () {
        initAll(document);

        var observer = new MutationObserver(function (mutations) {
            mutations.forEach(function (mutation) {
                mutation.addedNodes.forEach(function (node) {
                    if (node.nodeType === 1) {
                        initAll(node);
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true,
        });
    });
})();
