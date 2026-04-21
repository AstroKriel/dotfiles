(message "keybindings.el loaded!")

(map! :leader
      :desc "Find file"   "f f" #'consult-find
      :desc "Live grep"   "f g" #'consult-ripgrep
      :desc "Find buffer" "f b" #'consult-buffer
      :desc "Toggle file explorer" "e" #'treemacs)

(map! :n "K" #'lsp-ui-doc-show)
(map! :n "<leader>k" #'lsp-ui-doc-hide)

