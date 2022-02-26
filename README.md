# Quoridor
Python으로 구현한 보드게임 쿼리도

> 💡 미완성된 게임입니다.

Python IDLE 에서 플레이 할 수 있는 쿼리도 입니다.

미완성이기 때문에 GUI가 존재하지 않습니다. ㅠㅠ

다음과 같이 플레이 할 수 있습니다.

```python
>>> from quoridor import Game

>>> game = Game()

>>> game.start()
```

```python
>>> game.move('e8')
>>> game.move('e7h') # e7 에 장애물을 수평으로 설치
>>> game.move('a1v') # a1 에 장애물을 수직으로 설치
```
