// Sample Java file with some issues
public class Calculator {
    public static double calculateAverage(int[] numbers) {
        int total = 0;
        for (int i = 0; i < numbers.length; i++) {
            total += numbers[i];
        }
        return total / numbers.length;
    }
    
    public static int findMax(int[] numbers) {
        int maxNum = 0;
        for (int num : numbers) {
            if (num > maxNum) {
                maxNum = num;
            }
        }
        return maxNum;
    }
    
    public static int[] filterPositive(int[] numbers) {
        int[] result = new int[numbers.length];
        int count = 0;
        for (int num : numbers) {
            if (num > 0) {
                result[count] = num;
                count++;
            }
        }
        return result;
    }
    
    public static void main(String[] args) {
        // Bug: division by zero if empty array
        int[] emptyArray = {};
        double avg = calculateAverage(emptyArray);
        System.out.println("Average: " + avg);
        
        // Bug: maxNum starts at 0, fails for negative numbers
        int[] negatives = {-5, -2, -10};
        int max = findMax(negatives);
        System.out.println("Max: " + max);
        
        // Bug: array has null values for unfilled positions
        int[] mixed = {1, -2, 3, -4, 5};
        int[] positive = filterPositive(mixed);
        for (int num : positive) {
            System.out.print(num + " ");
        }
    }
}