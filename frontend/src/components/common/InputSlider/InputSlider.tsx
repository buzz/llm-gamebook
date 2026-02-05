import { Box, Group, Input, Slider } from '@mantine/core'
import { useEffect, useRef, useState } from 'react'
import type { BoxProps, SliderProps } from '@mantine/core'

import classes from './InputSlider.module.css'

const SNAP_RANGE_PX = 10

interface InputSliderProps extends Pick<SliderProps, 'marks' | 'max' | 'min'>, BoxProps {
  description?: string
  disabled?: boolean
  label: string
  onChange: (value: number) => void
  step?: number
  snapToMarks?: boolean
  value: number
}

function InputSlider({
  description,
  disabled,
  label,
  marks,
  max = 100,
  min = 0,
  onChange,
  step,
  snapToMarks = false,
  value,
  ...otherProps
}: InputSliderProps) {
  const [inputValue, setInputValue] = useState<string | number>(value)
  const [focused, setFocused] = useState(false)
  const [prevValue, setPrevValue] = useState(value)
  const [sliderWidth, setSliderWidth] = useState(0)
  const sliderContainerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!sliderContainerRef.current) {
      return
    }

    const updateSliderWidth = () => {
      const width = sliderContainerRef.current?.offsetWidth ?? 0
      if (width > 0) {
        setSliderWidth(width)
      }
    }

    updateSliderWidth()

    const resizeObserver = new ResizeObserver(() => {
      updateSliderWidth()
    })

    resizeObserver.observe(sliderContainerRef.current)

    window.addEventListener('resize', updateSliderWidth)

    return () => {
      resizeObserver.disconnect()
      window.removeEventListener('resize', updateSliderWidth)
    }
  }, [snapToMarks, marks])

  const snapToNearestMark = (val: number): number => {
    if (!marks || marks.length === 0 || !snapToMarks) {
      return val
    }

    let currentSliderWidth = sliderWidth
    if (currentSliderWidth === 0 && sliderContainerRef.current) {
      currentSliderWidth = sliderContainerRef.current.offsetWidth
      if (currentSliderWidth > 0) {
        setSliderWidth(currentSliderWidth)
      }
    }

    if (currentSliderWidth === 0) {
      return val
    }

    const totalRange = max - min
    const snapRangeValue = (SNAP_RANGE_PX / currentSliderWidth) * totalRange

    let nearestMark = marks[0]
    for (let i = 1; i < marks.length; i++) {
      if (Math.abs(marks[i].value - val) < Math.abs(nearestMark.value - val)) {
        nearestMark = marks[i]
      }
    }

    if (Math.abs(nearestMark.value - val) <= snapRangeValue) {
      return nearestMark.value
    }

    return val
  }

  const handleSliderChange = (newValue: number) => {
    const snappedValue = snapToNearestMark(newValue)
    onChange(snappedValue)
  }

  // State Derivation Pattern (replaces useEffect)
  if (value !== prevValue) {
    setPrevValue(value)
    // Only sync the text input if the user ISN'T currently typing in it
    if (!focused) {
      setInputValue(value)
    }
  }

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const rawValue = event.target.value
    setInputValue(rawValue)

    if (rawValue === '' || rawValue === '-') {
      return
    }

    const numValue = Number.parseFloat(rawValue)

    if (!Number.isNaN(numValue)) {
      // We clamp here to update the slider position while typing,
      // but we do NOT touch 'inputValue' so the user can type freely (e.g. "105")
      const clamped = Math.min(max, Math.max(min, numValue))
      onChange(clamped)
    }
  }

  const handleBlur = () => {
    setFocused(false)

    // On blur, we force the input to match the strictly valid value
    let numValue = Number.parseFloat(inputValue.toString())
    if (Number.isNaN(numValue)) {
      numValue = value
    }
    const clamped = Math.min(max, Math.max(min, numValue))

    onChange(clamped)
    setInputValue(clamped)
  }

  return (
    <Box {...otherProps}>
      <Input.Label>{label}</Input.Label>
      {description ? <Input.Description>{description}</Input.Description> : null}
      <Group align="center">
        <Input
          className={classes.input}
          disabled={disabled}
          type="text"
          inputSize="5"
          size="xs"
          value={inputValue}
          onChange={handleInputChange}
          onFocus={() => {
            setFocused(true)
          }}
          onBlur={handleBlur}
        />
        <div ref={sliderContainerRef} className={classes.sliderWrapper}>
          <Slider
            className={classes.slider}
            label={null}
            min={min}
            max={max}
            marks={marks}
            disabled={disabled}
            onChange={handleSliderChange}
            step={step}
            value={value}
          />
        </div>
      </Group>
    </Box>
  )
}

export default InputSlider
