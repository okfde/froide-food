/*

https://github.com/bloodyowl/scroll
Copyright (c) 2015 Matthias Le Brun

*/

const createAnimation = (func, duration = 300) => new Promise((resolve) => {
  const startDate = Date.now()
  const tick = () => {
    const progress = Math.min(1, (Date.now() - startDate) / duration)
    func(progress)
    if (progress < 1) {
      window.requestAnimationFrame(tick)
    } else {
      resolve()
    }
  }
  tick()
})

const smoothScroll = ({
  x = window.pageXOffset,
  y = window.pageYOffset
}, duration) => {
  const initialTop = window.pageYOffset
  const initialLeft = window.pageXOffset
  return createAnimation((progress) => {
    window.scrollTo(
      (1 - progress) * initialLeft + x * progress,
      (1 - progress) * initialTop + y * progress
    )
  }, duration)
}

export default smoothScroll
