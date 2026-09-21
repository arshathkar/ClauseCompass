import { validateFile } from './validate';
import { extractPdf } from './pdf';
import { extractDocx } from './docx';
import { extractTextPlain } from './text';

export async function extractText(file: File, onProgress?: (page: number, total: number) => void) {
  const type = await validateFile(file);
  
  if (type === 'application/pdf') {
    return extractPdf(file, onProgress);
  } else if (type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
    return extractDocx(file);
  } else {
    return extractTextPlain(file);
  }
}
