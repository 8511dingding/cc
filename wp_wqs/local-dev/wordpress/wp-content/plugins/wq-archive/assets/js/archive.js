/**
 * 王庆松艺术档案库 — 前端交互脚本
 * 无刷新筛选与分页加载
 */
(function($) {
    'use strict';

    var WQArchive = {
        currentPage: 1,
        isLoading: false,
        hasMore: true,

        $grid: null,
        $loadMore: null,
        $noResults: null,
        $resultsCount: null,

        init: function() {
            this.$grid = $('#wq-archive-grid');
            this.$loadMore = $('#wq-archive-load-more');
            this.$noResults = $('#wq-archive-no-results');
            this.$resultsCount = $('#wq-archive-results-count');

            this.bindEvents();
            this.loadInitial();
        },

        bindEvents: function() {
            var self = this;

            $('.wq-archive__tab').on('click', function() {
                var postType = $(this).data('post-type');
                self.switchTab(postType);
            });

            $('#wq-archive-type-filter, #wq-archive-year-filter').on('change', function() {
                self.currentPage = 1;
                self.loadResults();
            });

            $('#wq-archive-search').on('keypress', function(e) {
                if (e.which === 13) {
                    self.currentPage = 1;
                    self.loadResults();
                }
            }).on('blur', function() {
                self.currentPage = 1;
                self.loadResults();
            });

            this.$loadMore.on('click', function() {
                self.loadMore();
            });
        },

        switchTab: function(postType) {
            $('.wq-archive__tab')
                .removeClass('wq-archive__tab--active')
                .attr('aria-selected', 'false');

            $('.wq-archive__tab[data-post-type="' + postType + '"]')
                .addClass('wq-archive__tab--active')
                .attr('aria-selected', 'true');

            window.wqArchive.currentPostType = postType;
            this.currentPage = 1;
            this.loadResults();
        },

        loadInitial: function() {
            this.loadResults();
        },

        loadResults: function() {
            var self = this;

            if (this.isLoading) return;
            this.isLoading = true;

            var postType = window.wqArchive.currentPostType || 'artwork';
            var typeFilter = $('#wq-archive-type-filter').val();
            var yearFilter = $('#wq-archive-year-filter').val();
            var searchQuery = $('#wq-archive-search').val();

            this.$grid.html(
                '<div class="wq-archive__loading" aria-busy="true">' +
                '<span class="wq-archive__loading-text">加载中...</span>' +
                '</div>'
            );
            this.$noResults.attr('hidden', true);
            this.$loadMore.attr('hidden', true);

            $.ajax({
                url: window.wqArchive.ajaxUrl,
                type: 'POST',
                dataType: 'json',
                data: {
                    action: 'wq_archive_fetch_results',
                    nonce: window.wqArchive.nonce,
                    post_type: postType,
                    item_type: typeFilter,
                    creation_year: yearFilter,
                    s: searchQuery,
                    page: this.currentPage,
                    posts_per_page: window.wqArchive.postsPerPage || 12
                },
                success: function(response) {
                    if (response.success) {
                        self.renderResults(response.data);
                    } else {
                        self.$grid.html(
                            '<div class="wq-archive__no-results">' +
                            '<p>加载失败，请重试。</p>' +
                            '</div>'
                        );
                    }
                },
                error: function() {
                    self.$grid.html(
                        '<div class="wq-archive__no-results">' +
                        '<p>网络错误，请重试。</p>' +
                        '</div>'
                    );
                },
                complete: function() {
                    self.isLoading = false;
                }
            });
        },

        loadMore: function() {
            var self = this;
            this.currentPage++;

            if (this.isLoading) return;
            this.isLoading = true;

            this.$loadMore.prop('disabled', true).text('加载中...');

            var postType = window.wqArchive.currentPostType || 'artwork';
            var typeFilter = $('#wq-archive-type-filter').val();
            var yearFilter = $('#wq-archive-year-filter').val();
            var searchQuery = $('#wq-archive-search').val();

            $.ajax({
                url: window.wqArchive.ajaxUrl,
                type: 'POST',
                dataType: 'json',
                data: {
                    action: 'wq_archive_fetch_results',
                    nonce: window.wqArchive.nonce,
                    post_type: postType,
                    item_type: typeFilter,
                    creation_year: yearFilter,
                    s: searchQuery,
                    page: this.currentPage,
                    posts_per_page: window.wqArchive.postsPerPage || 12
                },
                success: function(response) {
                    if (response.success) {
                        self.appendResults(response.data);
                    } else {
                        self.currentPage--;
                    }
                },
                error: function() {
                    self.currentPage--;
                },
                complete: function() {
                    self.isLoading = false;
                    self.$loadMore.prop('disabled', false).text('加载更多');
                }
            });
        },

        renderResults: function(data) {
            if (!data.items || data.items.length === 0) {
                this.$grid.empty();
                this.$noResults.removeAttr('hidden');
                this.$resultsCount.text('0 项结果');
                this.hasMore = false;
                return;
            }

            this.hasMore = data.has_more;
            this.$resultsCount.text(data.total + ' 项结果');

            var html = '';
            for (var i = 0; i < data.items.length; i++) {
                html += this.renderCard(data.items[i]);
            }
            this.$grid.html(html);

            if (this.hasMore) {
                this.$loadMore.removeAttr('hidden');
            } else {
                this.$loadMore.attr('hidden', true);
            }
        },

        appendResults: function(data) {
            if (!data.items || data.items.length === 0) {
                this.hasMore = false;
                this.$loadMore.attr('hidden', true);
                return;
            }

            this.hasMore = data.has_more;
            var html = '';
            for (var i = 0; i < data.items.length; i++) {
                html += this.renderCard(data.items[i]);
            }
            this.$grid.append(html);

            if (!this.hasMore) {
                this.$loadMore.attr('hidden', true);
            }
        },

        renderCard: function(item) {
            var imageHtml;
            if (item.thumbnail) {
                imageHtml = '<img class="wq-archive__card-image" src="' + item.thumbnail + '" alt="' + item.title + '">';
            } else {
                imageHtml = '<div class="wq-archive__card-image--placeholder">—</div>';
            }

            return '<a href="' + item.url + '" class="wq-archive__card">' +
                '<div class="wq-archive__card-image-wrap">' +
                imageHtml +
                '</div>' +
                '<div class="wq-archive__card-info">' +
                '<h3 class="wq-archive__card-title">' + item.title + '</h3>' +
                '<p class="wq-archive__card-meta">' + item.meta + '</p>' +
                '</div>' +
                '</a>';
        }
    };

    $(document).ready(function() {
        if ($('#wq-archive-grid').length) {
            WQArchive.init();
        }
    });

})(jQuery);