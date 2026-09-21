export async function validateFile(file: File) {
  if (file.size > 10 * 1024 * 1024) {
    throw new Error('File is too large (max 10MB)');
  }
  
  // Magic bytes check
  const buffer = await file.slice(0, 4).arrayBuffer();
  const arr = new Uint8Array(buffer);
  
  // %PDF-
  if (arr[0] === 0x25 && arr[1] === 0x50 && arr[2] === 0x44 && arr[3] === 0x46) {
    return 'application/pdf';
  }
  
  // PK\x03\x04 (DOCX/ZIP)
  if (arr[0] === 0x50 && arr[1] === 0x4B && arr[2] === 0x03 && arr[3] === 0x04) {
    return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
  }

  if (file.type === 'text/plain' || file.name.endsWith('.txt') || file.name.endsWith('.md')) {
    return 'text/plain';
  }
  
  throw new Error('Unsupported file type. Please upload a PDF, DOCX, or TXT file.');
}
