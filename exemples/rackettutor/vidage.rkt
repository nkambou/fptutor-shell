#lang racket/base
;; Vidage de l'arbre : Racket lit sa propre syntaxe, et la rend en JSON.
;; Remplace le lecteur de s-expressions ecrit en Python.
;;   racket vidage.rkt fichier.rkt
(require json racket/list)

(define (en-json d)
  (cond [(null? d) '()]
        [(pair? d) (map en-json (if (list? d) d (list (car d) (cdr d))))]
        [(boolean? d) (if d "#t" "#f")]
        [(string? d) (format "~s" d)]
        [else (format "~a" d)]))

(define (lire-tout port)
  ;; la ligne #lang n'est pas une donnee lisible : on la saute
  (define premiere (peek-char port))
  (let boucle ([acc '()])
    (define d (with-handlers ([exn:fail:read? (lambda (e) (read-line port) 'saute)])
                (read port)))
    (cond [(eof-object? d) (reverse acc)]
          [(eq? d 'saute) (boucle acc)]
          [else (boucle (cons d acc))])))

(module+ main
  (define chemin (vector-ref (current-command-line-arguments) 0))
  (write-json (map en-json (call-with-input-file chemin lire-tout))))
