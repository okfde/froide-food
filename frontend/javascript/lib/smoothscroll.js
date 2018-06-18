/*
Modified from
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
  y = window.pageYOffset,
  el = window
}, duration) => {
  let initialTop
  let initialLeft
  if (el === window) {
    initialTop = window.pageYOffset
    initialLeft = window.pageXOffset
  } else {
    initialTop = el.scrollTop
    initialLeft = el.scrollLeft
  }
  return createAnimation((progress) => {
    let offsetX = (1 - progress) * initialLeft + x * progress
    let offsetY = (1 - progress) * initialTop + y * progress
    if (el === window) {
      window.scrollTo(offsetX, offsetY)
    } else {
      el.scrollLeft = offsetX
      el.scrollTop = offsetY
    }
  }, duration)
}

export default smoothScroll
