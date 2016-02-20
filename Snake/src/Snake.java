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
    public Point head;
    public int length;
    public int starvation;
    Snake(){
        //this is the main snake constructor
        head = new Point(0,0);
        length = 3; // start with a length of 3
        starvation = 5; // start with 5 turns before you die of food
    }
    
    public void eat(){
        length++;
        starvation = starvation+5;
    }
    public void move(int newx,int newy){
        head.translate(newx, newy);
    }
}
