/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

import java.awt.Point;
/**
 *
 * @author joelnewman
 */


public class Mainloop {
    boolean dead;
    Snake henery;
    int[][] board;
    int totalX = 100;
    int totalY = 100;
    Mainloop() {
        //Mainloop constructor
        System.out.println("I am in the mainloop constructor");
        henery = new Snake();
        dead = false;
        board = new int[totalX][totalY];
    }

    /**
     * This method will be used to get the information from the webserver or
     * whatever method we get for finding out where food and other snakes are
     */
    public void pullSnakeBoard() {
        System.out.println("I am in pullSnakeBoard");
        for(int tempX = 0;tempX<totalX;tempX++){
            for(int tempY = 0;tempY<totalY;tempY++){
                // loop over the array and do some stuff
                board[tempX][tempY] = 0;
            }
        }
    }

    /**
     * This method will explicitly check to see if there is a snake that we can
     * eat/kill 
     * If there is a snake we can kill it will return True
     * if there is not a snake we can kill it will return False
     * 
     * @return boolean
     */
    public boolean killSnake() {
        System.out.println("I can kill another snake");
        //read through board, can I kill some other snake?
        return true;
    }

    /**
     * This will retrun the location of the food 
     * 
     * Returns a Point object
     * @return
     */
    public Point locateFood() {
        System.out.println("I found food");
        // parse the grid and return a point that contains the food coordinates
        Point food = new Point(3, 4);
        return food;
    }
    
    /**
     * Main starting point that the driver calls
     */
    public void start(){
        Point[] board = new Point[100];
        while(!dead){
            pullSnakeBoard();
            dead = true;
            
            
        }
    }
    
}
