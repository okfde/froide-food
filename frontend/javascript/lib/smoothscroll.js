/*
Modified from
https://github.com/bloodyowl/scroll
Copyright (c) 2015 Matthias Le Brun

*/

const MAX_DISTANCE_THRESHOLD = 800

const createAnimation = (func, duration = 300) =>
  new Promise((resolve) => {
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

const scrollTo = function (el, offsetX, offsetY) {
  if (el === window) {
    window.scrollTo(offsetX, offsetY)
  } else {
    el.scrollLeft = offsetX
    el.scrollTop = offsetY
  }
}

const smoothScroll = (
  { x = window.pageXOffset, y = window.pageYOffset, el = window },
  duration
) => {
  let initialTop
  let initialLeft
  if (el === window) {
    initialTop = window.pageYOffset
    initialLeft = window.pageXOffset
  } else {
    initialTop = el.scrollTop
    initialLeft = el.scrollLeft
  }
  const maxDistance = Math.max(Math.abs(initialTop - y), Math.abs(initialLeft, x))
  if (maxDistance > MAX_DISTANCE_THRESHOLD) {
    scrollTo(el, x, y)
  }
  return createAnimation((progress) => {
    const offsetX = (1 - progress) * initialLeft + x * progress
    const offsetY = (1 - progress) * initialTop + y * progress
    scrollTo(el, offsetX, offsetY)
  }, duration)
}

export default smoothScroll
