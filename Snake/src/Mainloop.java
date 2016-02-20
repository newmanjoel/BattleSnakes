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

public class Mainloop {
    boolean dead;
    Snake henery;
    Mainloop() {
        //Mainloop constructor
        System.out.println("I am in the mainloop constructor");
        henery = new Snake();
        dead = false;
    }

    public Point[] pullSnakeBoard() {
        System.out.println("I am in pullSnakeBoard");
        Point p1 = new Point(1, 1);
        Point p2 = new Point(2, 2);
        Point[] points = new Point[2];
        points[0] = p1;
        points[1] = p2;
        return points;
    }

    public boolean killSnake(Point[] board) {
        System.out.println("I can kill another snake");
        //read through board, can I kill some other snake?
        return true;
    }

    public Point locateFood() {
        System.out.println("I found food");
        // parse the grid and return a point that contains the food coordinates
        Point food = new Point(3, 4);
        return food;
    }
    
    public void start(){
        Point[] board = new Point[100];
        while(!dead){
            board = pullSnakeBoard();
            dead = true;
            
            
        }
    }
    
}
