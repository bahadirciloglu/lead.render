#!/bin/bash
# =============================================================================
# LEAD DISCOVERY API - TEST RUNNER SCRIPT
# =============================================================================
# Comprehensive test execution script
# =============================================================================

set -e

echo "🧪 LEAD DISCOVERY API - TEST SUITE"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} ✅ $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} ⚠️  $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} ❌ $1"
}

# Test execution function
run_test_suite() {
    local test_type=$1
    local test_file=$2
    local description=$3
    
    print_status "Running $description tests..."
    
    if [ -f "tests/$test_file" ]; then
        pytest tests/$test_file -v --tb=short --durations=10
        if [ $? -eq 0 ]; then
            print_success "$description tests passed"
        else
            print_error "$description tests failed"
            return 1
        fi
    else
        print_warning "$description test file not found: tests/$test_file"
    fi
    
    return 0
}

# Main test execution
main() {
    local test_type="${1:-all}"
    
    case $test_type in
        "unit")
            print_status "Running UNIT tests only"
            run_test_suite "unit" "test_unit.py" "Unit"
            ;;
        "integration"|"basic")
            print_status "Running INTEGRATION tests only"
            run_test_suite "integration" "test_integration_simple.py" "Integration"
            ;;
        "e2e")
            print_status "Running E2E tests only"
            run_test_suite "e2e" "test_e2e_simple.py" "E2E"
            ;;
        "all")
            print_status "Running ALL tests"
            
            # Unit Tests
            run_test_suite "unit" "test_unit.py" "Unit" || exit 1
            
            # Integration Tests
            run_test_suite "integration" "test_integration_simple.py" "Integration" || exit 1
            
            # E2E Tests
            run_test_suite "e2e" "test_e2e_simple.py" "E2E" || exit 1
            
            print_success "All test suites completed successfully! 🎉"
            ;;
        *)
            print_error "Invalid test type: $test_type"
            echo "Usage: $0 [unit|integration|e2e|basic|all]"
            exit 1
            ;;
    esac
}

# Run main function with provided arguments
main "$@"

echo ""
print_status "Test execution completed"
echo "📊 Test Results Summary:"
echo "  - Unit Tests: Isolated component testing"
echo "  - Integration Tests: Real database and API testing"
echo "  - E2E Tests: Complete workflow validation"
echo ""
echo "📁 Test files location: tests/"
echo "�� Test configuration: pytest.ini"
echo "📦 Test dependencies: test-requirements.txt"
