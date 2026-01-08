/**
 * Download Utilities for Charts and Reports
 * Supports PNG and PDF export
 */

import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

/**
 * Download a DOM element as PNG image
 */
export async function downloadAsPNG(
  element: HTMLElement,
  filename: string = 'chart'
): Promise<void> {
  try {
    const canvas = await html2canvas(element, {
      backgroundColor: '#111827',
      scale: 2,
      logging: false,
      useCORS: true,
    });

    canvas.toBlob((blob) => {
      if (!blob) return;
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${filename}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    });
  } catch (error) {
    console.error('Error downloading PNG:', error);
    throw error;
  }
}

/**
 * Download a DOM element as PDF
 */
export async function downloadAsPDF(
  element: HTMLElement,
  filename: string = 'report',
  orientation: 'portrait' | 'landscape' = 'portrait'
): Promise<void> {
  try {
    const canvas = await html2canvas(element, {
      backgroundColor: '#111827',
      scale: 2,
      logging: false,
      useCORS: true,
    });

    const imgData = canvas.toDataURL('image/png');
    const imgWidth = orientation === 'portrait' ? 210 : 297;
    const imgHeight = orientation === 'portrait' ? 297 : 210;
    const ratio = canvas.width / canvas.height;
    
    let width = imgWidth - 20;
    let height = width / ratio;
    
    if (height > imgHeight - 20) {
      height = imgHeight - 20;
      width = height * ratio;
    }

    const pdf = new jsPDF({
      orientation,
      unit: 'mm',
      format: 'a4',
    });

    pdf.addImage(imgData, 'PNG', 10, 10, width, height);
    pdf.save(`${filename}.pdf`);
  } catch (error) {
    console.error('Error downloading PDF:', error);
    throw error;
  }
}

/**
 * Download complete dashboard as PDF
 */
export async function downloadDashboardAsPDF(
  elements: HTMLElement[],
  filename: string = 'dashboard'
): Promise<void> {
  try {
    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4',
    });

    for (let i = 0; i < elements.length; i++) {
      if (i > 0) pdf.addPage();

      const canvas = await html2canvas(elements[i], {
        backgroundColor: '#111827',
        scale: 2,
        logging: false,
        useCORS: true,
      });

      const imgData = canvas.toDataURL('image/png');
      const imgWidth = 190;
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      
      pdf.addImage(imgData, 'PNG', 10, 10, imgWidth, imgHeight);
    }

    pdf.save(`${filename}.pdf`);
  } catch (error) {
    console.error('Error downloading dashboard PDF:', error);
    throw error;
  }
}

/**
 * Download chart data as CSV
 */
export function downloadAsCSV(
  data: any[],
  columns: string[],
  filename: string = 'data'
): void {
  try {
    const headers = columns.join(',');
    const rows = data.map(row => 
      columns.map(col => {
        const value = row[col];
        if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
          return `"${value.replace(/"/g, '""')}"`;
        }
        return value;
      }).join(',')
    );
    
    const csv = [headers, ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${filename}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Error downloading CSV:', error);
    throw error;
  }
}

/**
 * Generate sanitized filename from text
 */
export function sanitizeFilename(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .substring(0, 50);
}