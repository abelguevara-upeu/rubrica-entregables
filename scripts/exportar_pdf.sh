#!/bin/sh
# Abre un DOCX en Word, actualiza el índice, lo guarda y genera su PDF.   uso: sh exportar_pdf.sh ruta/al/archivo.docx
d="$1"; pdf="${d%.docx}.pdf"
osascript <<EOF
with timeout of 900 seconds
  tell application "Microsoft Word"
    activate
    open POSIX file "$d"
    delay 3
    set doc to active document
    try
      repeat with t in (tables of contents of doc)
        update t
      end repeat
    end try
    save as doc file name "$pdf" file format format PDF
    save doc
    close doc saving no
  end tell
end timeout
EOF
