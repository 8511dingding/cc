(function() {
    'use strict';

    function initShareDialog() {
        var dialog = document.getElementById('wqs-share-dialog');
        if (!dialog || dialog.dataset.wqsShareReady === '1') {
            return;
        }
        dialog.dataset.wqsShareReady = '1';

        var surface = dialog.querySelector('.wqs-share-dialog__surface');
        var closeButton = dialog.querySelector('.wqs-share-dialog__close');
        var nativeButton = dialog.querySelector('.wqs-share-native');
        var mainContent = dialog.querySelectorAll(
            '.wqs-share-dialog__header, .wqs-share-dialog__preview, .wqs-share-primary-actions, .wqs-share-platforms, .wqs-share-utilities'
        );
        var qrSection = dialog.querySelector('.wqs-share-qr');
        var qrCode = dialog.querySelector('.wqs-share-qr__code');
        var toast = dialog.querySelector('.wqs-share-toast');
        var shareUrl = dialog.dataset.shareUrl;
        var shareTitle = dialog.dataset.shareTitle;
        var qrEnabled = dialog.dataset.qrEnabled !== '0';
        var toastTimer;
        var activeTrigger = null;

    function showToast(message) {
        window.clearTimeout(toastTimer);
        toast.textContent = message;
        toast.classList.add('is-visible');
        toastTimer = window.setTimeout(function() {
            toast.classList.remove('is-visible');
        }, 1800);
    }

    function copyLink() {
        var copy = navigator.clipboard && navigator.clipboard.writeText
            ? navigator.clipboard.writeText(shareUrl)
            : new Promise(function(resolve, reject) {
                var textarea = document.createElement('textarea');
                textarea.value = shareUrl;
                textarea.setAttribute('readonly', '');
                textarea.style.position = 'fixed';
                textarea.style.opacity = '0';
                document.body.appendChild(textarea);
                textarea.select();
                try {
                    document.execCommand('copy') ? resolve() : reject();
                } catch (error) {
                    reject(error);
                }
                textarea.remove();
            });

        copy.then(function() {
            showToast(document.documentElement.lang.indexOf('zh') === 0 ? '链接已复制' : 'Link copied');
        }).catch(function() {
            showToast(shareUrl);
        });
    }

    function setMainHidden(hidden) {
        mainContent.forEach(function(element) {
            element.hidden = hidden;
        });
    }

    function renderQr() {
        if (qrCode.dataset.rendered) {
            return;
        }
        qrCode.innerHTML = '';
        if (typeof window.QRCode === 'function') {
            new window.QRCode(qrCode, {
                text: shareUrl,
                width: 220,
                height: 220,
                colorDark: '#111111',
                colorLight: '#ffffff',
                correctLevel: window.QRCode.CorrectLevel.M
            });
            qrCode.dataset.rendered = '1';
        } else {
            qrCode.textContent = shareUrl;
        }
    }

    function showQr(platform) {
        if (!qrEnabled) {
            copyLink();
            return;
        }
        setMainHidden(true);
        qrSection.hidden = false;
        renderQr();
        dialog.querySelectorAll('.wqs-share-platform').forEach(function(button) {
            button.classList.toggle('is-selected', button.dataset.platform === platform);
        });
        qrSection.querySelector('.wqs-share-qr__back').focus();
    }

    function hideQr() {
        qrSection.hidden = true;
        setMainHidden(false);
        dialog.querySelectorAll('.wqs-share-platform').forEach(function(button) {
            button.classList.remove('is-selected');
        });
    }

    function openDialog(platform) {
        activeTrigger = document.activeElement;
        hideQr();
        if (typeof dialog.showModal === 'function') {
            dialog.showModal();
        } else {
            dialog.setAttribute('open', '');
        }
        document.documentElement.classList.add('wqs-share-is-open');

        if (platform) {
            var button = dialog.querySelector('[data-platform="' + platform + '"]');
            if (button && button.dataset.mode === 'qr') {
                showQr(platform);
                return;
            }
        }
        closeButton.focus();
    }

    function closeDialog() {
        if (typeof dialog.close === 'function') {
            dialog.close();
        } else {
            dialog.removeAttribute('open');
        }
        document.documentElement.classList.remove('wqs-share-is-open');
        hideQr();
    }

    document.querySelectorAll('.wqs-share-open').forEach(function(button) {
        button.addEventListener('click', function() {
            openDialog(button.dataset.platform || '');
        });
    });

    document.querySelectorAll('[data-wqs-direct-share]').forEach(function(link) {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            window.open(link.href, 'wqs-share', 'width=720,height=640,noopener,noreferrer');
        });
    });

    closeButton.addEventListener('click', closeDialog);
    dialog.addEventListener('click', function(event) {
        if (event.target === dialog) {
            closeDialog();
        }
    });
    dialog.addEventListener('close', function() {
        document.documentElement.classList.remove('wqs-share-is-open');
        if (activeTrigger && typeof activeTrigger.focus === 'function') {
            activeTrigger.focus();
        }
    });

    if (nativeButton && navigator.share) {
        nativeButton.classList.add('is-supported');
        nativeButton.addEventListener('click', function() {
            navigator.share({ title: shareTitle, url: shareUrl }).catch(function() {});
        });
    }

    dialog.querySelectorAll('.wqs-share-platform').forEach(function(button) {
        button.addEventListener('click', function() {
            if (button.dataset.mode === 'direct' && button.dataset.shareHref) {
                window.open(button.dataset.shareHref, 'wqs-share', 'width=720,height=640,noopener,noreferrer');
                return;
            }
            showQr(button.dataset.platform);
        });
    });

    dialog.querySelectorAll('.wqs-share-copy').forEach(function(button) {
        button.addEventListener('click', copyLink);
    });

    var showQrButton = dialog.querySelector('.wqs-share-show-qr');
    if (showQrButton) {
        showQrButton.addEventListener('click', function() {
            showQr('');
        });
    }

    dialog.querySelector('.wqs-share-qr__back').addEventListener('click', hideQr);

        surface.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                event.preventDefault();
                closeDialog();
            }
        });

    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initShareDialog, { once: true });
    } else {
        initShareDialog();
    }
})();
