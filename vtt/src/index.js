import React from 'react';
import ReactDOM from 'react-dom/client';

import { useSyncDemo } from '@tldraw/sync'
import { Tldraw } from 'tldraw'
import 'tldraw/tldraw.css'

function RuleBook() {
    return <object data="./rules.pdf" type="application/pdf" style={{width: "100%", height: "98vh"}} >Rule Book</object>
}

function MyTldraw() {
    const queryParameters = new URLSearchParams(window.location.search);
    const session = queryParameters.get("session");
    const store = useSyncDemo({ roomId:  session });
    return <div style={{ position: 'fixed', inset: 0, left: 270, top: 0 }}>
               <Tldraw store={store} />
           </div>
}

function MainPage() {
    if (document.getElementById('aspect_multi_target').checked) {
        return MyTldraw()
    } else {
        return RuleBook()
    }
}

const root = ReactDOM.createRoot(document.getElementById('tldraw_container'));
root.render(<MyTldraw />);
