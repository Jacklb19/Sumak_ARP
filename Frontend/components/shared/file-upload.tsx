"use client"

import { useCallback, useState } from "react"
import { useDropzone } from "react-dropzone"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { FileText, Upload, X, CheckCircle2 } from "lucide-react"
import { cn } from "@/lib/utils"

interface FileUploadProps {
  onFileSelect: (file: File | null) => void
  maxSize?: number
  accept?: Record<string, string[]>
}

export function FileUpload({
  onFileSelect,
  maxSize = 5 * 1024 * 1024,
  accept = { "application/pdf": [".pdf"] },
}: FileUploadProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [error, setError] = useState("")

  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: any[]) => {
      setError("")

      if (rejectedFiles.length > 0) {
        const rejection = rejectedFiles[0]
        if (rejection.errors[0]?.code === "file-too-large") {
          setError(`El archivo es muy grande. Máximo ${maxSize / (1024 * 1024)}MB`)
        } else if (rejection.errors[0]?.code === "file-invalid-type") {
          setError("Solo se permiten archivos PDF")
        } else {
          setError("Error al cargar el archivo")
        }
        return
      }

      if (acceptedFiles.length > 0) {
        const file = acceptedFiles[0]
        setSelectedFile(file)
        onFileSelect(file)
      }
    },
    [maxSize, onFileSelect],
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept,
    maxSize,
    multiple: false,
  })

  const removeFile = () => {
    setSelectedFile(null)
    onFileSelect(null)
    setError("")
  }

  return (
    <div className="space-y-2">
      {!selectedFile ? (
        <Card
          {...getRootProps()}
          className={cn(
            "border-2 border-dashed cursor-pointer transition-colors hover:border-primary/50",
            isDragActive && "border-primary bg-primary/5",
            error && "border-destructive",
          )}
        >
          <input {...getInputProps()} />
          <div className="p-8 text-center">
            <Upload className={cn("h-10 w-10 mx-auto mb-4", isDragActive ? "text-primary" : "text-muted-foreground")} />
            <p className="font-medium mb-1">
              {isDragActive ? "Suelta el archivo aquí" : "Arrastra tu CV o haz clic para seleccionar"}
            </p>
            <p className="text-sm text-muted-foreground">Solo archivos PDF, máximo {maxSize / (1024 * 1024)}MB</p>
          </div>
        </Card>
      ) : (
        <Card className="border-2 border-primary">
          <div className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                <FileText className="h-5 w-5 text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-sm truncate">{selectedFile.name}</p>
                <p className="text-xs text-muted-foreground">{(selectedFile.size / 1024).toFixed(1)} KB</p>
              </div>
              <CheckCircle2 className="h-5 w-5 text-green-600 flex-shrink-0" />
              <Button type="button" variant="ghost" size="sm" onClick={removeFile} className="flex-shrink-0">
                <X className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </Card>
      )}

      {error && <p className="text-sm text-destructive">{error}</p>}
    </div>
  )
}
