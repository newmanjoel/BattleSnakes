/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 *
 * @author joelnewman
 */
import java.awt.Point;

public class Snake {

    /**
     * Point object that contains the x,y coordinates of the snake head
     */
    public Point head;

    /**
     * This is the length of the snake
     */
    public int length;

    /**
     * This is how many turns we are from dying
     */
    public int starvation;
    
    /**
     * Empty Snake constuctor
     * makes the head a 0,0 with a length of 3 and a starvation time of 5
     */
    Snake(){
        //this is the main snake constructor
        head = new Point(0,0);
        length = 3; // start with a length of 3
        starvation = 5; // start with 5 turns before you die of food
    }
    
    /**
     * Call this method when we consume food or a snake
     * will increase the length by 1 and reset the starvation time
     */
    public void eat(){
        length++;
        starvation = starvation+5;
    }

    /**
     * Moves the head of the snake.
     * newx refers to the positive or negitive movement in the x direction
     * newy refers to the positive or negitive movement in the y direction
     * 
     * EX.
     * move(1,-1) when the head was at 5,4 would result in the head being at
     * 6,3
     * 
     * 
     * @param newx amount to move in x direction
     * @param newy amount to move in y direction
     */
    public void move(int newx,int newy){
        head.translate(newx, newy);
        
    }
}
