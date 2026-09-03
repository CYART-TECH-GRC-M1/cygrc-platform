"use client";
import React, { useCallback, useState } from "react";
import ProgressBar from "./ProgressBar";

type UploadItem = { id: string; file: File; progress: number; status: 'uploading' | 'done' | 'error'; };

export default function EvidenceUpload({ onComplete }: { onComplete?: () => void }) {
  const [uploads, setUploads] = useState<UploadItem[]>([]);

  const handleFiles = useCallback((files: FileList | null) => {
    if (!files) return;
    Array.from(files).forEach((file) => {
      const id = String(Date.now()) + '-' + file.name;
      const item: UploadItem = { id, file, progress: 0, status: 'uploading' };
      setUploads((s) => [item, ...s]);

      const reader = new FileReader();
      reader.onload = async () => {
        const dataUrl = reader.result as string;
        // simulate progress while uploading
        let progress = 0;
        setUploads((s) => s.map(u => u.id===id?{...u,progress}:u));
        const timer = setInterval(()=>{
          progress += Math.random()*10 + 5;
          setUploads((s)=>s.map(u=>u.id===id?{...u,progress:Math.min(95, Math.floor(progress))}:u));
        }, 250);

        try {
          const res = await fetch('/api/evidence', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: file.name, type: file.type, size: file.size, dataUrl }) });
          clearInterval(timer);
          if (!res.ok) throw new Error('Upload failed');
          setUploads((s)=>s.map(u=>u.id===id?{...u,progress:100,status:'done'}:u));
          onComplete && onComplete();
        } catch (err) {
          clearInterval(timer);
          setUploads((s)=>s.map(u=>u.id===id?{...u,progress:0,status:'error'}:u));
        }
      };
      reader.readAsDataURL(file);
    });
  }, [onComplete]);

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    handleFiles(e.dataTransfer.files);
  };

  return (
    <div>
      <div onDrop={onDrop} onDragOver={(e)=>e.preventDefault()} className="rounded-2xl border-dashed border-2 border-slate-700 bg-slate-900/40 p-6 text-center">
        <p className="text-sm text-slate-300">Drag & drop files here, or <label htmlFor="evidence-input" className="cursor-pointer text-sky-300 hover:underline">browse</label></p>
        <input id="evidence-input" type="file" multiple className="sr-only" onChange={(e)=>handleFiles(e.target.files)} />
      </div>

      <div className="mt-4 space-y-3">
        {uploads.map(u=> (
          <div key={u.id} className="rounded-lg bg-slate-900/50 p-3">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-slate-100">{u.file.name}</div>
                <div className="text-xs text-slate-400">{(u.file.size/1024).toFixed(1)} KB</div>
              </div>
              <div className="ml-4 w-48">
                <ProgressBar value={u.progress} />
              </div>
            </div>
            {u.status==='error' && <div className="mt-2 text-xs text-rose-400">Upload failed</div>}
          </div>
        ))}
      </div>
    </div>
  );
}
