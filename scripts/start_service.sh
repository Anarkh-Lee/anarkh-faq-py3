#!/bin/bash

echo "Starting FAQ Retrieval Service..."

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 激活虚拟环境（如果存在）
if [ -f "../policy-py/.venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source "../policy-py/.venv/bin/activate"
else
    echo "Virtual environment not found, using system Python..."
fi

# 切换到项目目录
cd "$SCRIPT_DIR"

echo "Environment setup complete!"
echo

# 显示菜单
while true; do
    echo "========================================"
    echo "FAQ Retrieval Service Manager"
    echo "========================================"
    echo "1. Start API service"
    echo "2. Initialize FAQ data via API"
    echo "3. Test MySQL connection"
    echo "4. Check service health"
    echo "5. Exit"
    echo "========================================"
    read -p "Please select an option (1-5): " choice

    case $choice in
        1)
            echo
            echo "Starting API service..."
            echo "Note: The service will auto-load the embedding model on startup."
            echo "Once started, you can initialize data via API: POST /api/v1/faqs/initialize"
            cd "$SCRIPT_DIR/.."
            python run.py
            if [ $? -ne 0 ]; then
                echo "Failed to start service!"
                read -p "Press Enter to continue..."
                continue
            fi
            ;;
        2)
            echo
            echo "Initializing FAQ data via API..."
            echo "Make sure the API service is running first!"
            echo "Calling: POST http://localhost:5000/api/v1/faqs/initialize"
            curl -X POST http://localhost:5000/api/v1/faqs/initialize -H "Content-Type: application/json" -d '{"recreate_collection": true}'
            if [ $? -ne 0 ]; then
                echo "Failed to initialize via API! Make sure the service is running."
                read -p "Press Enter to continue..."
                continue
            fi
            echo "Data initialization completed via API!"
            read -p "Press Enter to continue..."
            ;;
        3)
            echo
            echo "Testing MySQL connection..."
            cd "$SCRIPT_DIR/.."
            python tests/test_mysql.py
            if [ $? -ne 0 ]; then
                echo "MySQL connection test failed!"
                read -p "Press Enter to continue..."
                continue
            fi
            echo "MySQL connection test completed!"
            read -p "Press Enter to continue..."
            ;;
        4)
            echo
            echo "Checking service health..."
            echo "Calling: GET http://localhost:5000/health"
            curl -X GET http://localhost:5000/health
            if [ $? -ne 0 ]; then
                echo "Health check failed! Make sure the service is running."
                read -p "Press Enter to continue..."
                continue
            fi
            echo
            echo "Health check completed!"
            read -p "Press Enter to continue..."
            ;;
        5)
            echo "Goodbye!"
            break
            ;;
        *)
            echo "Invalid option, please try again."
            ;;
    esac
done
