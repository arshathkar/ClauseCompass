export async function extractPdf(file: File, onProgress?: (page: number, total: number) => void): Promise<{text: string, pageCount: number}> {
  const pdfjsLib = await import('pdfjs-dist');
  
  // Configure worker
  pdfjsLib.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.mjs`;
  
  const arrayBuffer = await file.arrayBuffer();
  
  const loadingTask = pdfjsLib.getDocument({
    data: arrayBuffer,
    isEvalSupported: false
  });
  
  const pdf = await loadingTask.promise;
  const numPages = pdf.numPages;
  
  let fullText = '';
  let totalChars = 0;
  
  for (let i = 1; i <= numPages; i++) {
    const page = await pdf.getPage(i);
    const textContent = await page.getTextContent();
    
    // Sort items by Y, then X for logical reading order
    const items = textContent.items as any[];
    items.sort((a, b) => {
      if (Math.abs(a.transform[5] - b.transform[5]) > 5) {
        return b.transform[5] - a.transform[5];
      }
      return a.transform[4] - b.transform[4];
    });
    
    let pageText = `[[page:${i}]]\n`;
    let lastY = -1;
    
    for (const item of items) {
      if (lastY !== -1 && Math.abs(item.transform[5] - lastY) > 5) {
        pageText += '\n';
      }
      pageText += item.str;
      lastY = item.transform[5];
    }
    
    fullText += pageText + '\n\n';
    totalChars += pageText.length;
    
    if (onProgress) {
      onProgress(i, numPages);
    }
  }
  
  const avgCharsPerPage = totalChars / numPages;
  if (avgCharsPerPage < 200) {
    throw new Error('This looks like a scanned document. Please paste the text directly.');
  }
  
  return {
    text: fullText,
    pageCount: numPages
  };
}
