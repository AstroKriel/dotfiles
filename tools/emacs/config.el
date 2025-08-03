;; Theme
(setq doom-theme 'doom-one)

;; Line numbers (relative like in Neovim)
(setq display-line-numbers-type 'relative)

;; Clipboard and behavior tweaks
(setq select-enable-clipboard t
      confirm-kill-emacs nil)

;; LSP tweaks (like your LSP floating options)
(after! lsp-ui
  (setq lsp-ui-doc-position 'at-point
        lsp-ui-doc-show-with-cursor t
        lsp-ui-doc-border "white"))

;; Show invisible characters (similar to listchars)
(setq whitespace-style '(face tabs spaces trailing lines-tail))
(global-whitespace-mode 1)

(load-theme 'catppuccin :no-confirm)

(load! "keybindings")
