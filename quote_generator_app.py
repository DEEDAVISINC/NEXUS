#!/usr/bin/env python3
"""
SIMPLE QUOTE GENERATOR - Just paste and click!
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import subprocess
import os
import tempfile
from pathlib import Path


class QuoteGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DEE DAVIS INC - Quote Generator")
        self.root.geometry("900x700")
        
        # Header
        header = tk.Frame(root, bg="#1e3a8a", height=80)
        header.pack(fill=tk.X)
        
        title_label = tk.Label(
            header,
            text="🚀 QUOTE REQUEST GENERATOR",
            font=("Arial", 24, "bold"),
            bg="#1e3a8a",
            fg="white"
        )
        title_label.pack(pady=20)
        
        subtitle = tk.Label(
            header,
            text="Paste your info below and click Generate!",
            font=("Arial", 12),
            bg="#1e3a8a",
            fg="white"
        )
        subtitle.pack()
        
        # Main content area
        content = tk.Frame(root, padx=20, pady=20)
        content.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        instructions = tk.Label(
            content,
            text="Paste your quote information below (or use the template button):",
            font=("Arial", 12, "bold"),
            anchor="w"
        )
        instructions.pack(fill=tk.X, pady=(0, 10))
        
        # Text area
        self.text_area = scrolledtext.ScrolledText(
            content,
            wrap=tk.WORD,
            width=100,
            height=25,
            font=("Courier", 11)
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Load template text
        self.load_template()
        
        # Button frame
        button_frame = tk.Frame(content)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Template button
        template_btn = tk.Button(
            button_frame,
            text="📋 Load Template",
            command=self.load_template,
            font=("Arial", 12),
            bg="#6b7280",
            fg="white",
            padx=20,
            pady=10
        )
        template_btn.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        clear_btn = tk.Button(
            button_frame,
            text="🗑️ Clear",
            command=self.clear_text,
            font=("Arial", 12),
            bg="#6b7280",
            fg="white",
            padx=20,
            pady=10
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Generate button (big and prominent)
        generate_btn = tk.Button(
            button_frame,
            text="✨ GENERATE QUOTE REQUEST",
            command=self.generate_quote,
            font=("Arial", 14, "bold"),
            bg="#16a34a",
            fg="white",
            padx=30,
            pady=15
        )
        generate_btn.pack(side=tk.RIGHT, padx=5)
        
        # Status label
        self.status_label = tk.Label(
            content,
            text="Ready to generate quote requests",
            font=("Arial", 10),
            fg="#6b7280"
        )
        self.status_label.pack(pady=5)
        
    def load_template(self):
        """Load the template into the text area"""
        template = """RFQ_NUMBER: RFQ-2026-001
TITLE: Quote Request Title
ISSUE_DATE: January 26, 2026
DUE_DATE: February 5, 2026
DUE_TIME: 5:00 PM EST
CONTRACT_PERIOD: 12 months

COLOR_SCHEME: 1
(1=Navy/Gold, 2=Brown/Orange, 3=Purple/Violet, 4=Blue/Teal, 5=Dark Brown)

INTRODUCTION:
DEE DAVIS INC is seeking competitive quotes for a Michigan municipal client. Paste your introduction here...

SCOPE:
Describe what the vendor needs to provide...

KEY_REQUIREMENTS:
- Requirement 1
- Requirement 2
- Requirement 3

ITEMS:
1 | Item Description | Specifications | Quantity | unit
2 | Another Item | Specs | Qty | unit
3 | Third Item | Details | Amount | unit
"""
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, template)
        self.status_label.config(text="Template loaded - edit and click Generate!", fg="#16a34a")
    
    def clear_text(self):
        """Clear the text area"""
        if messagebox.askyesno("Clear", "Clear all text?"):
            self.text_area.delete(1.0, tk.END)
            self.status_label.config(text="Text cleared", fg="#6b7280")
    
    def generate_quote(self):
        """Generate the quote request"""
        # Get text
        text = self.text_area.get(1.0, tk.END).strip()
        
        if not text:
            messagebox.showerror("Error", "Please paste your quote information first!")
            return
        
        # Update status
        self.status_label.config(text="⚙️ Generating quote request...", fg="#d97706")
        self.root.update()
        
        try:
            # Create temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(text)
                temp_file = f.name
            
            # Generate the quote
            result = subprocess.run(
                ['python3', 'create_from_paste.py', 'rfq', temp_file],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            # Clean up temp file
            os.unlink(temp_file)
            
            if result.returncode == 0:
                # Success!
                self.status_label.config(text="✅ SUCCESS! Quote request generated!", fg="#16a34a")
                
                # Find generated files
                output_lines = result.stdout.split('\n')
                files_found = []
                
                for line in output_lines:
                    if '.html' in line or '.pdf' in line:
                        for word in line.split():
                            if ('.html' in word or '.pdf' in word) and not word.startswith('python'):
                                files_found.append(word.strip('•').strip())
                
                # Show success message
                msg = "✅ Quote request generated successfully!\n\n"
                msg += "Files created:\n"
                for f in files_found:
                    msg += f"  • {f}\n"
                msg += "\nCheck your NEXUS BACKEND folder!"
                
                messagebox.showinfo("Success!", msg)
                
                # Open the folder
                folder = os.path.dirname(os.path.abspath(__file__))
                subprocess.run(['open', folder])
                
            else:
                # Error
                self.status_label.config(text="❌ Error generating quote", fg="#dc2626")
                messagebox.showerror("Error", f"Failed to generate quote:\n\n{result.stderr}")
        
        except Exception as e:
            self.status_label.config(text="❌ Error occurred", fg="#dc2626")
            messagebox.showerror("Error", f"An error occurred:\n\n{str(e)}")


def main():
    root = tk.Tk()
    app = QuoteGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
