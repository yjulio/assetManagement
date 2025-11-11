#!/usr/bin/env python3
"""
Quick Code Generator CLI
Usage: ./generate.py <table_name> [options]
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.code_generator import CodeGenerator


def print_banner():
    """Print banner"""
    print("""
╔═══════════════════════════════════════════════════════╗
║       🤖 AUTOMATIC CODE GENERATOR                     ║
║       Generate CRUD code from database schema         ║
╚═══════════════════════════════════════════════════════╝
""")


def main():
    print_banner()
    
    if len(sys.argv) < 2:
        print("Usage: ./generate.py <table_name> [--routes] [--templates] [--save]")
        print("\nOptions:")
        print("  --routes      Generate Flask routes")
        print("  --templates   Generate HTML templates")
        print("  --save        Save files to disk")
        print("  --all         Generate everything and save")
        print("\nExamples:")
        print("  ./generate.py employees --all")
        print("  ./generate.py departments --routes --save")
        print("  ./generate.py inventory --templates")
        
        # List available tables
        try:
            generator = CodeGenerator()
            tables = generator.get_all_tables()
            generator.close()
            
            print(f"\n📋 Available tables ({len(tables)}):")
            for table in tables:
                print(f"  - {table}")
        except Exception as e:
            print(f"\n⚠️  Could not list tables: {e}")
        
        sys.exit(1)
    
    table_name = sys.argv[1]
    args = sys.argv[2:]
    
    generate_routes = '--routes' in args or '--all' in args
    generate_templates = '--templates' in args or '--all' in args
    save_files = '--save' in args or '--all' in args
    
    if not generate_routes and not generate_templates:
        generate_routes = True
        generate_templates = True
    
    print(f"📦 Generating code for table: {table_name}")
    print(f"   Routes: {'✅' if generate_routes else '❌'}")
    print(f"   Templates: {'✅' if generate_templates else '❌'}")
    print(f"   Save files: {'✅' if save_files else '❌'}")
    print()
    
    try:
        generator = CodeGenerator()
        
        # Check if table exists
        tables = generator.get_all_tables()
        if table_name not in tables:
            print(f"❌ Error: Table '{table_name}' not found!")
            print(f"\nAvailable tables: {', '.join(tables)}")
            generator.close()
            sys.exit(1)
        
        files_created = []
        
        # Generate routes
        if generate_routes:
            print("🔧 Generating routes...")
            routes_code = generator.generate_all_routes(table_name)
            
            if save_files:
                routes_file = f'src/generated_routes_{table_name}.py'
                with open(routes_file, 'w') as f:
                    f.write("# Auto-generated routes - Copy these into app.py\n\n")
                    f.write(routes_code)
                files_created.append(routes_file)
                print(f"   ✅ Saved to: {routes_file}")
            else:
                print("\n" + "="*80)
                print("ROUTES CODE:")
                print("="*80)
                print(routes_code)
        
        # Generate templates
        if generate_templates:
            print("\n🎨 Generating templates...")
            
            add_template = generator.generate_add_template(table_name)
            list_template = generator.generate_list_template(table_name)
            
            if save_files:
                add_file = f'src/templates/{table_name}_add.html'
                list_file = f'src/templates/{table_name}_list.html'
                
                with open(add_file, 'w') as f:
                    f.write(add_template)
                with open(list_file, 'w') as f:
                    f.write(list_template)
                
                files_created.append(add_file)
                files_created.append(list_file)
                
                print(f"   ✅ Saved to: {add_file}")
                print(f"   ✅ Saved to: {list_file}")
            else:
                print("\n" + "="*80)
                print("ADD TEMPLATE:")
                print("="*80)
                print(add_template)
                
                print("\n" + "="*80)
                print("LIST TEMPLATE:")
                print("="*80)
                print(list_template)
        
        generator.close()
        
        print("\n" + "="*80)
        print("✅ CODE GENERATION COMPLETE!")
        print("="*80)
        
        if files_created:
            print(f"\n📁 Created {len(files_created)} file(s):")
            for file in files_created:
                print(f"   - {file}")
            
            print("\n📝 Next steps:")
            if generate_routes:
                print(f"   1. Copy routes from src/generated_routes_{table_name}.py into src/app.py")
            if generate_templates:
                print(f"   2. Access templates at /{table_name} after adding routes")
            print("   3. Restart Flask to apply changes")
            print("   4. Test the new CRUD operations")
        else:
            print("\n💡 Use --save flag to save files automatically")
        
        print("\n🎉 Happy coding!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
