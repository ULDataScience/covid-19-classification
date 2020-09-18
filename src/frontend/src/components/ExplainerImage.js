import React, { useState } from 'react'
import { ReactComponent as XRayIcon } from '../assets/x-ray.svg'

function ExplainerImage (props) {
  const src = props.src
  const name = props.name
  const [loading, setLoading] = useState(true)

  return (
    <>
      <div style={{
        textAlign: 'center',
        display: loading ? 'none' : 'block'
      }}
      >
        <img
          src={src}
          style={{ width: '250px' }}
          onLoad={() => setLoading(false)}
        />
        <br />
        {loading ? '' : name}
      </div> {loading ? (
        <div style={{
          width: '250px',
          height: '250px',
          border: '2px dotted black',
          padding: '2px',
          textAlign: 'center'
        }}
        >
          <XRayIcon
            style={{
              width: '242px',
              height: '242px',
              opacity: '0.05'
            }}
          />
          {name}
        </div>
      ) : ''}
    </>

  )
}

export default ExplainerImage
