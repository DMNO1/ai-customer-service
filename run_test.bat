@echo off
cd /d "%~dp0"
py -c "import sys; sys.path.insert(0, 'services'); from vector_store_service import VectorStoreService; print('✓ VectorStoreService import successful')"
pause