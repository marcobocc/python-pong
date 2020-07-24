# Project created by Marco Bocchetti

import arcade

def clamp(value, lower, higher):
    return max(lower, min(value, higher))

class Paddle:
    def __init__(self, position):
        self.position = position
        self.size = [10, 80]
        self.speed = 800

    def move_up(self, deltaTime):
        self.position[1] += self.speed * deltaTime

    def move_down(self, deltaTime):
        self.position[1] -= self.speed * deltaTime

    def render(self, deltaTime):
        arcade.draw_rectangle_filled(self.position[0], self.position[1], self.size[0], self.size[1], arcade.color.WHITE)

class Ball:
    def __init__(self, position):
        self.position = position
        self.radius = 5
        self.def_velocity = [200, 200]
        self.velocity = [200, 200]
        self.velocity_multiplier = [1.05, 1.05]

    def bounce_horizontal(self):
        self.velocity[0] *= -self.velocity_multiplier[1]

    def bounce_vertical(self):
        self.velocity[1] *= -self.velocity_multiplier[1]

    def move(self, deltaTime):
        self.position[0] += self.velocity[0] * deltaTime
        self.position[1] += self.velocity[1] * deltaTime

    def render(self, deltaTime):
        arcade.draw_circle_filled(self.position[0], self.position[1], self.radius, arcade.color.WHITE)

class Player:
    def __init__(self, id, paddle):
        self.id = id
        self.score = 0
        self.record = 0
        self.paddle = paddle

    def move_paddle_key(self, deltaTime, key_up_pressed, key_down_pressed):
        if key_up_pressed and not key_down_pressed:
            self.paddle.move_up(deltaTime)
        elif key_down_pressed and not key_up_pressed:
            self.paddle.move_down(deltaTime)

    def move_paddle_cheat(self, ball_position):
        self.paddle.position[1] = ball_position[1]

    def handle_victory(self):
        self.score += 1
        self.record = max(self.score, self.record)

class Pong(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height, "Pong!")
        self.width = width
        self.height = height
        self.sound = arcade.Sound("sound.mp3")
        self.restart()
        self.set_mouse_visible(False)
        arcade.set_background_color((20, 20, 20))
        arcade.schedule(self.loop, 1.0 / 120.0)

    def restart(self):
        self.ball = Ball([self.width / 2, self.height / 2])
        self.lpaddle = Paddle([10 / 2, self.height / 2])
        self.rpaddle = Paddle([self.width - 10 / 2, self.height / 2])
        self.player0 = Player(0, self.lpaddle)
        self.player1 = Player(1, self.rpaddle)
        self.curr_screen = 0 # 0: main menu - 1: playing - 2: paused
        self.key_w_pressed = 0
        self.key_s_pressed = 0
        self.key_up_pressed = 0
        self.key_down_pressed = 0
        self.is_playing_against_bot = 0

    def loop(self, deltaTime):
        arcade.start_render()
        # if in main menu
        if self.curr_screen == 0:
            if self.key_up_pressed or self.key_down_pressed:
                self.is_playing_against_bot = self.key_down_pressed
                self.sound.play(0.03, 0)
                self.curr_screen = 1
            self.render_menu_screen(deltaTime)
        # if playing or if paused
        elif self.curr_screen == 1 or self.curr_screen == 2:
            if self.curr_screen == 1:
                self.update_paddles(deltaTime)
                self.update_ball(deltaTime)
            elif self.curr_screen == 2:
                self.render_paused_screen(deltaTime)
            self.render_score(deltaTime)
            self.ball.render(deltaTime)
            self.lpaddle.render(deltaTime)
            self.rpaddle.render(deltaTime)

    def update_paddles(self, deltaTime):
        self.player0.move_paddle_key(deltaTime, self.key_w_pressed, self.key_s_pressed)
        self.player0.paddle.position[1] = clamp(self.player0.paddle.position[1], 0, self.height)
        if self.is_playing_against_bot:
            self.player1.paddle.position[1] = self.ball.position[1]
        else:
            self.player1.move_paddle_key(deltaTime, self.key_up_pressed, self.key_down_pressed)
            self.player1.paddle.position[1] = clamp(self.player1.paddle.position[1], 0, self.height)

    def update_ball(self, deltaTime):
        self.ball.move(deltaTime)
        # horizontal collision checking
        if self.ball.position[0] < self.ball.radius / 2.0 + self.lpaddle.size[0]:
            if (self.ball.position[1] < self.lpaddle.position[1] + self.lpaddle.size[1] / 2
            and self.ball.position[1] > self.lpaddle.position[1] - self.lpaddle.size[1] / 2):
                # left paddle caught the ball
                self.ball.position[0] = self.ball.radius / 2.0 + self.lpaddle.size[0];
                self.ball.bounce_horizontal()
                if self.is_playing_against_bot:
                    self.player0.handle_victory()
                self.sound.play(0.03, 0)
            else:
                # left paddle missed the ball
                self.player1.handle_victory()
                if self.is_playing_against_bot:
                    self.player0.score = 0
                self.reset_ball()
        elif self.ball.position[0] > self.width - self.ball.radius / 2.0 - self.rpaddle.size[0]:
            if (self.ball.position[1] < self.rpaddle.position[1] + self.rpaddle.size[1] / 2
            and self.ball.position[1] > self.rpaddle.position[1] - self.rpaddle.size[1] / 2):
                # right paddle caught the ball
                self.ball.position[0] = self.width - self.ball.radius / 2.0 - self.rpaddle.size[0]
                self.ball.bounce_horizontal()
                self.sound.play(0.03, 0)
            else:
                # right paddle missed the ball
                self.player0.handle_victory()
                self.reset_ball()
        # vertical collision checking
        if self.ball.position[1] < self.ball.radius / 2.0:
            self.ball.position[1] = self.ball.radius / 2.0
            self.ball.bounce_vertical()
        elif self.ball.position[1] > self.height - self.ball.radius / 2.0:
            self.ball.position[1] = self.height - self.ball.radius / 2.0
            self.ball.bounce_vertical()

    # resets ball back in the middle of the screen, and throws it in the opposite direction
    def reset_ball(self):
        self.ball.position[0] = self.width / 2
        self.ball.position[1] = self.height / 2
        sign = lambda x: (1, -1)[x < 0]
        self.ball.velocity[0] = -sign(self.ball.velocity[0]) * self.ball.def_velocity[0]
        self.ball.velocity[1] = -sign(self.ball.velocity[1]) * self.ball.def_velocity[1]

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            self.key_up_pressed = 1
        elif key == arcade.key.DOWN:
            self.key_down_pressed = 1
        elif key == arcade.key.W:
            self.key_w_pressed = 1
        elif key == arcade.key.S:
            self.key_s_pressed = 1
        elif key == arcade.key.SPACE:
            if self.curr_screen == 1:
                self.curr_screen = 2
                self.sound.play(0.03, 0)
            elif self.curr_screen == 2:
                self.curr_screen = 1
                self.sound.play(0.03, 0)
        elif key == arcade.key.ESCAPE:
            self.restart()
            self.sound.play(0.03, 0)

    def on_key_release(self, key, modifiers):
        if key == arcade.key.UP:
            self.key_up_pressed = 0
        elif key == arcade.key.DOWN:
            self.key_down_pressed = 0
        elif key == arcade.key.W:
            self.key_w_pressed = 0
        elif key == arcade.key.S:
            self.key_s_pressed = 0

    def render_menu_screen(self, deltaTime):
        arcade.draw_text("PRESS ARROW UP TO PLAY AGAINST A FRIEND!", self.width/2, self.height/2+8, arcade.color.WHITE, font_size=16, anchor_x="center")
        arcade.draw_text("PRESS ARROW DOWN TO PLAY AGAINST AN UNBEATABLE FOE!", self.width/2, self.height/2-32, arcade.color.WHITE, font_size=16, anchor_x="center")

    def render_score(self, deltaTime):
        if self.is_playing_against_bot:
            arcade.draw_text("SCORE: " + str(self.player0.score), self.width/2, self.height-50, arcade.color.WHITE, font_size=16, anchor_x="center")
            arcade.draw_text("RECORD: " + str(self.player0.record), self.width/2, self.height-72, arcade.color.WHITE, font_size=16, anchor_x="center")
        else:
            arcade.draw_text(str(self.player0.score) + " - " + str(self.player1.score), self.width/2, self.height-50, arcade.color.WHITE, font_size=16, anchor_x="center")

    def render_paused_screen(self, deltaTime):
        arcade.draw_text("GAME PAUSED", self.width/2, self.height/2+8, arcade.color.WHITE, font_size=16, anchor_x="center")
        arcade.draw_text("PRESS SPACE TO CONTINUE", self.width/2, self.height/2-32, arcade.color.WHITE, font_size=16, anchor_x="center")

if __name__ == "__main__":
    Pong(600, 400)
    arcade.run()
