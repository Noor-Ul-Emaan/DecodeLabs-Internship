// Sample JavaScript file with some issues
function calculateAverage(numbers) {
    let total = 0;
    for (let i = 0; i <= numbers.length; i++) {
        total += numbers[i];
    }
    return total / numbers.length;
}

function findMax(numbers) {
    let maxNum = 0;
    for (let num of numbers) {
        if (num > maxNum) {
            maxNum = num;
        }
    }
    return maxNum;
}

function processData(arr) {
    // Inefficient: creating multiple loops
    let sum = 0;
    for (let i = 0; i < arr.length; i++) {
        sum += arr[i];
    }
    
    let avg = sum / arr.length;
    
    let max = arr[0];
    for (let i = 1; i < arr.length; i++) {
        if (arr[i] > max) {
            max = arr[i];
        }
    }
    
    return { sum, avg, max };
}

// Bug: loop goes out of bounds
const avg = calculateAverage([1, 2, 3]);
console.log(`Average: ${avg}`);

// Bug: maxNum starts at 0, fails for negative numbers
const max = findMax([-5, -2, -10]);
console.log(`Max: ${max}`);