(function ($, wp, config) {
    'use strict';

    if (!config) {
        return;
    }

    var translationFocusHandled = false;

    function enhanceTranslationFields() {
        $('.tr_lang').each(function () {
            var input = $(this);
            if (input.data('wqs-enhanced')) {
                return;
            }

            input.data('wqs-enhanced', true);
            input.attr('placeholder', '搜索并选择已有文章');

            var row = input.closest('tr');
            var language = input.attr('id').replace('tr_lang_', '');
            var hiddenInput = $('#htr_lang_' + language);
            var editCell = row.find('.pll-edit-column');
            var createLink = row.find('td.hidden a').first();

            if (!input.prev('.wqs-translation-field-label').length) {
                input.before('<span class="wqs-translation-field-label">优先关联已有文章</span>');
            }

            if (!row.find('.wqs-translation-status').length) {
                $('<span class="wqs-translation-status" aria-live="polite"></span>')
                    .insertAfter(input);
            }

            if (createLink.length && !row.find('.wqs-create-translation').length) {
                $('<a class="wqs-create-translation">没有合适文章，创建新翻译</a>')
                    .attr('href', createLink.attr('href'))
                    .insertAfter(row.find('.wqs-translation-status'));
            }

            if ($.fn.autocomplete && !input.autocomplete('instance')) {
                input.autocomplete({
                    minLength: 0,
                    source: function (request, response) {
                        $.getJSON(config.ajaxUrl, {
                            action: 'pll_posts_not_translated',
                            post_language: $('.post_lang_choice').val(),
                            translation_language: language,
                            post_type: config.postType,
                            term: request.term,
                            pll_post_id: $('#post_ID').val() || config.postId,
                            _pll_nonce: $('#_pll_nonce').val()
                        }).done(response);
                    },
                    select: function (event, ui) {
                        hiddenInput.val(ui.item.id);
                        if (ui.item.link) {
                            editCell.html(ui.item.link);
                        }
                    }
                });
            }

            input.off('autocompleteselect.wqs').on('autocompleteselect.wqs', function (event, ui) {
                var selectedId = ui && ui.item ? parseInt(ui.item.id, 10) : 0;
                var status = row.find('.wqs-translation-status');

                if (!selectedId || !config.postId) {
                    return;
                }

                status.removeClass('is-error is-success').addClass('is-saving').text('正在关联...');

                $.post(config.ajaxUrl, {
                    action: 'wqs_link_post_translation',
                    nonce: config.linkNonce,
                    post_id: config.postId,
                    translation_id: selectedId,
                    target_language: language
                }).done(function (result) {
                    if (!result || !result.success) {
                        status.removeClass('is-saving is-success').addClass('is-error')
                            .text(result && result.data && result.data.message ? result.data.message : '关联失败。');
                        return;
                    }

                    hiddenInput.val(selectedId);
                    status.removeClass('is-saving is-error').addClass('is-success')
                        .text('已关联，文章内容可正常保存。');
                }).fail(function (xhr) {
                    var message = xhr.responseJSON && xhr.responseJSON.data && xhr.responseJSON.data.message
                        ? xhr.responseJSON.data.message
                        : '关联失败，请重试。';
                    status.removeClass('is-saving is-success').addClass('is-error').text(message);
                });
            });

            if (!parseInt(hiddenInput.val(), 10)) {
                editCell.find('a').off('click.wqs').on('click.wqs', function (event) {
                    event.preventDefault();
                    input.trigger('focus');
                    if ($.fn.autocomplete) {
                        input.autocomplete('search', input.val());
                    }
                });
            }
        });

        var translations = $('.translations');
        if (translations.length && !translations.find('.wqs-translation-help').length) {
            translations.prepend(
                '<p class="wqs-translation-help">先搜索并关联已经存在的中英文文章；选择后会立即保存关联。确认没有对应文章时，再使用“创建新翻译”。</p>'
            );
        }

        if (config.focusTranslation && !translationFocusHandled) {
            var firstEmpty = $('.tr_lang').filter(function () {
                var language = this.id.replace('tr_lang_', '');
                return !parseInt($('#htr_lang_' + language).val(), 10);
            }).first();

            if (firstEmpty.length) {
                translationFocusHandled = true;
                firstEmpty.trigger('focus');
                if ($.fn.autocomplete) {
                    firstEmpty.autocomplete('search', '');
                }
            }
        }
    }

    function interceptPostListCreateLinks() {
        $('#the-list a[href*="post-new.php"][href*="from_post="]').each(function () {
            var link = $(this);
            if (link.data('wqs-intercepted')) {
                return;
            }

            var url;
            try {
                url = new URL(link.attr('href'), window.location.origin);
            } catch (error) {
                return;
            }

            var sourcePostId = url.searchParams.get('from_post');
            if (!sourcePostId) {
                return;
            }

            link.data('wqs-intercepted', true);
            link.attr('title', '先选择已有翻译文章');
            link.on('click.wqs', function (event) {
                event.preventDefault();
                window.location.href = config.adminPostUrl +
                    '?post=' + encodeURIComponent(sourcePostId) +
                    '&action=edit&wqs_link_translation=1';
            });
        });
    }

    function registerCategoryPanel() {
        if (
            !wp ||
            !wp.plugins ||
            !wp.element ||
            !wp.components ||
            !wp.data
        ) {
            return;
        }

        var PluginDocumentSettingPanel = wp.editPost && wp.editPost.PluginDocumentSettingPanel;
        if (!PluginDocumentSettingPanel) {
            return;
        }

        var el = wp.element.createElement;
        var useEffect = wp.element.useEffect;
        var useMemo = wp.element.useMemo;
        var useState = wp.element.useState;
        var CheckboxControl = wp.components.CheckboxControl;
        var SearchControl = wp.components.SearchControl;
        var useSelect = wp.data.useSelect;
        var useDispatch = wp.data.useDispatch;

        function CategoryPanel() {
            var selectedIds = useSelect(function (select) {
                return select('core/editor').getEditedPostAttribute('categories') || [];
            }, []);
            var editPost = useDispatch('core/editor').editPost;
            var languageState = useState(config.language || $('.post_lang_choice').val() || '');
            var language = languageState[0];
            var setLanguage = languageState[1];
            var searchState = useState('');
            var search = searchState[0];
            var setSearch = searchState[1];
            var categories = config.categories[language] || config.categories.all || [];

            useEffect(function () {
                function handleLanguageChange(event) {
                    if (event.detail && event.detail.lang) {
                        setLanguage(event.detail.lang.slug || '');
                    }
                }

                document.addEventListener('onPostLangChoice', handleLanguageChange);
                return function () {
                    document.removeEventListener('onPostLangChoice', handleLanguageChange);
                };
            }, []);

            var visibleCategories = useMemo(function () {
                var normalizedSearch = search.trim().toLocaleLowerCase();
                var byId = {};

                categories.forEach(function (category) {
                    byId[category.id] = category;
                });

                return categories
                    .filter(function (category) {
                        if (!normalizedSearch) {
                            return true;
                        }
                        return category.name.toLocaleLowerCase().indexOf(normalizedSearch) !== -1 ||
                            category.slug.toLocaleLowerCase().indexOf(normalizedSearch) !== -1;
                    })
                    .map(function (category) {
                        var depth = 0;
                        var parentId = category.parent;
                        var seen = {};

                        while (parentId && byId[parentId] && !seen[parentId] && depth < 6) {
                            seen[parentId] = true;
                            depth++;
                            parentId = byId[parentId].parent;
                        }

                        return Object.assign({}, category, { depth: depth });
                    });
            }, [categories, search]);

            function toggleCategory(categoryId, checked) {
                var nextIds = selectedIds.slice();
                if (checked && nextIds.indexOf(categoryId) === -1) {
                    nextIds.push(categoryId);
                } else if (!checked) {
                    nextIds = nextIds.filter(function (id) {
                        return id !== categoryId;
                    });
                }
                editPost({ categories: nextIds });
            }

            return el(
                PluginDocumentSettingPanel,
                {
                    name: 'wqs-post-categories',
                    title: '文章分类',
                    className: 'wqs-category-panel'
                },
                el(SearchControl, {
                    label: '搜索分类',
                    value: search,
                    onChange: setSearch,
                    placeholder: '按名称或别名搜索'
                }),
                !visibleCategories.length
                    ? el('p', { className: 'wqs-category-empty' }, '没有找到分类。')
                    : null,
                el(
                    'div',
                    { className: 'wqs-category-list' },
                    visibleCategories.map(function (category) {
                        return el(CheckboxControl, {
                            key: category.id,
                            label: (category.depth ? Array(category.depth + 1).join('— ') : '') + category.name,
                            checked: selectedIds.indexOf(category.id) !== -1,
                            onChange: function (checked) {
                                toggleCategory(category.id, checked);
                            }
                        });
                    })
                )
            );
        }

        wp.plugins.registerPlugin('wqs-editor-categories', {
            render: CategoryPanel,
            icon: 'category'
        });
    }

    function registerCreatedAtPanel() {
        if (
            !wp ||
            !wp.plugins ||
            !wp.element ||
            !wp.components ||
            !wp.data ||
            !wp.editPost ||
            !wp.editPost.PluginDocumentSettingPanel
        ) {
            return;
        }

        var el = wp.element.createElement;
        var useEffect = wp.element.useEffect;
        var useSelect = wp.data.useSelect;
        var useDispatch = wp.data.useDispatch;
        var TextControl = wp.components.TextControl;
        var PluginDocumentSettingPanel = wp.editPost.PluginDocumentSettingPanel;

        function normalizeForInput(value) {
            return value ? value.replace(' ', 'T').slice(0, 16) : '';
        }

        function normalizeForStorage(value) {
            return value ? value.replace('T', ' ') + ':00' : '';
        }

        function CreatedAtPanel() {
            var meta = useSelect(function (select) {
                return select('core/editor').getEditedPostAttribute('meta') || {};
            }, []);
            var editPost = useDispatch('core/editor').editPost;
            var createdAt = meta._wqs_created_at || '';

            useEffect(function () {
                if (createdAt || !config.currentTime) {
                    return;
                }

                editPost({
                    meta: Object.assign({}, meta, {
                        _wqs_created_at: config.currentTime
                    })
                });
            }, []);

            return el(
                PluginDocumentSettingPanel,
                {
                    name: 'wqs-created-at',
                    title: '内容创建时间',
                    className: 'wqs-created-at-panel'
                },
                el(TextControl, {
                    label: '原始创建时间',
                    type: 'datetime-local',
                    value: normalizeForInput(createdAt || config.currentTime),
                    onChange: function (value) {
                        editPost({
                            meta: Object.assign({}, meta, {
                                _wqs_created_at: normalizeForStorage(value)
                            })
                        });
                    },
                    help: '用于网站列表的日期、年份筛选和排序；修改“发布”时间不会改变这里。'
                })
            );
        }

        wp.plugins.registerPlugin('wqs-editor-created-at', {
            render: CreatedAtPanel,
            icon: 'calendar-alt'
        });
    }

    function registerCreationYearPanel() {
        if (
            !wp ||
            !wp.plugins ||
            !wp.element ||
            !wp.components ||
            !wp.data ||
            !wp.editPost ||
            !wp.editPost.PluginDocumentSettingPanel
        ) {
            return;
        }

        var el = wp.element.createElement;
        var useEffect = wp.element.useEffect;
        var useSelect = wp.data.useSelect;
        var useDispatch = wp.data.useDispatch;
        var TextControl = wp.components.TextControl;
        var PluginDocumentSettingPanel = wp.editPost.PluginDocumentSettingPanel;

        function CreationYearPanel() {
            var meta = useSelect(function (select) {
                return select('core/editor').getEditedPostAttribute('meta') || {};
            }, []);
            var editPost = useDispatch('core/editor').editPost;
            var creationYear = meta._wqs_creation_year || '';

            useEffect(function () {
                if (creationYear) {
                    return;
                }

                editPost({
                    meta: Object.assign({}, meta, {
                        _wqs_creation_year: new Date().getFullYear()
                    })
                });
            }, []);

            return el(
                PluginDocumentSettingPanel,
                {
                    name: 'wqs-creation-year',
                    title: '创作年份',
                    className: 'wqs-creation-year-panel'
                },
                el(TextControl, {
                    label: '年份',
                    type: 'number',
                    min: 1900,
                    max: new Date().getFullYear() + 10,
                    step: 1,
                    value: creationYear || '',
                    onChange: function (value) {
                        var year = parseInt(value, 10);
                        editPost({
                            meta: Object.assign({}, meta, {
                                _wqs_creation_year: Number.isFinite(year) ? year : 0
                            })
                        });
                    },
                    help: '用于左侧年份菜单、下拉筛选、列表排序和年份展示。'
                })
            );
        }

        wp.plugins.registerPlugin('wqs-editor-creation-year', {
            render: CreationYearPanel,
            icon: 'calendar'
        });
    }

    $(function () {
        if (config.isList) {
            interceptPostListCreateLinks();
            new MutationObserver(interceptPostListCreateLinks).observe(
                document.getElementById('the-list'),
                { childList: true, subtree: true }
            );
        }

        if (config.isEditor) {
            registerCategoryPanel();
            registerCreatedAtPanel();
            registerCreationYearPanel();
            enhanceTranslationFields();

            var attempts = 0;
            var translationTimer = window.setInterval(function () {
                attempts++;
                enhanceTranslationFields();
                if ($('.tr_lang').length || attempts >= 20) {
                    window.clearInterval(translationTimer);
                }
            }, 250);

            document.addEventListener('onPostLangChoice', function () {
                window.setTimeout(enhanceTranslationFields, 100);
            });
        }
    });
})(window.jQuery, window.wp, window.wqsEditorTools);
