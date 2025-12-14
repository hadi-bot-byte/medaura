print("1. Storage System")  
print("2. Calculator")  
choice = input("Choose: ")  
if choice == "1":  
    import sys  
    sys.path.append("src")  
    from storage_system import main as storage_main  
    storage_main.main() 
