export async function extractDocx(file: File): Promise<{text: string, pageCount: number}> {
  const mammoth = await import('mammoth');
  const arrayBuffer = await file.arrayBuffer();
  
  const result = await mammoth.extractRawText({ arrayBuffer });
  
  return {
    text: `[[page:1]]\n${result.value}`,
    pageCount: 1 // DOCX doesn't have reliable page counts via mammoth raw text
  };
}
