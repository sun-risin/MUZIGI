import React, { useState, useEffect } from 'react';
import Chat from './essential/Chat';
import Emotion from './essential/Emotion';
import Sidebar from './essential/Sidebar';
import './MainPage.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faBars } from '@fortawesome/free-solid-svg-icons';

function MainPage({ setIsLoggedIn }) { 
   const [isSidebarOpen, setIsSidebarOpen] = useState(false);
   const [messages, setMessages] = useState([]); // 모든 채팅 메시지 관리
   const [selectedChatId, setSelectedChatId] = useState(null);
   const [playlistTracks, setPlaylistTracks] = useState([]);//좋아요
   const [isFreshLogin, setIsFreshLogin] = useState(false); // 404 타이밍 버그 해결용
  
   //1. 재생목록 조회 api 호출
   const fetchPlaylists = async() =>{
    console.log("백엔드 좋아요 목록 새로고침");
    const muzigiToken = localStorage.getItem('accessToken');
    const spotifyToken = localStorage.getItem('spotifyAccessToken');

    if (!muzigiToken || !spotifyToken) return;

    //api 추가
    //const response = await fetch('');
    //const allTracks=await response.json();
    //setPlaylistTracks(allTracks);
   };

   const handleToggleLike = async(track)=>{
    console.log("'좋아요' 이벤트 받음", track.title);
    const muzigiToken = localStorage.getItem('accessToken');
    const emotion = track.emotion;
    const isAlreadyLiked = playlistTracks.find(item => item.trackId === track.trackId);
    try {
        if (isAlreadyLiked) {
          console.log("좋아요 취소 API 호출 (DELETE)");
            // api 작성
            // await fetch(`http://localhost:5000/api/playlist/${emotion}/remove`, { 
            //   method: 'DELETE',
            //   headers: { 'Authorization': `${muzigiToken}`, ... },
            //   body: JSON.stringify({ trackId: track.trackId })
            // });
          } else {
          console.log("좋아요 추가 API 호출 (POST)");
            // await fetch(`http://localhost:5000/api/playlist/${emotion}/add`, { 
            //   method: 'POST',
            //   headers: { 'Authorization': `${muzigiToken}`, ... },
            //   body: JSON.stringify(track) 
            // });
          }
          if (isAlreadyLiked) {
            setPlaylistTracks(prev => prev.filter(item => item.trackId !== track.trackId));
          } else {
            setPlaylistTracks(prev => [...prev, track]);
          }
        }catch(error){
          console.error("좋아요 api 오류", error);
        }
      };
   
    //재생목록 생성 api 호출
    const callNewPlaylist = async(spotifyToken)=>{
      const MuzigiToken = localStorage.getItem('accessToken');

      if(!muzigiToken || !spotifyToken){
        console.warn("muzigi토큰 or spotify 토큰이 없어 재생목록을 생성할 수 없음.");
        return;
      }
      try{
        console.log("감정별 재생목록 생성 시도...");
        const response = await fetch('http://localhost:5000/api/playlist/new',{
          method : 'POST',
          headers:{
            'Content-Type': 'application/json',
            'Authorization': `${muzigiToken}`
          },
          body: JSON.stringify({
            'spotifyToken':spotifyToken
          })
        });

        if (response.status === 201) { // 201: 새로 생성됨 [cite: 109]
        console.log("재생목록이 성공적으로 생성되었습니다.");
        // TODO: (다음 단계) 응답으로 온 ID들로 사이드바 '재생 목록' 상태 업데이트 [cite: 62]
        } else if (response.status === 200) {
          console.log("재생목록이 이미 존재합니다.");
        } else {
          const errorData = await response.json();
          console.error("재생목록 생성 실패:", errorData.error);
        }
      } catch (error) {
        console.error("재생목록 생성 API 호출 실패:", error);
      }
    };

   useEffect(() => {
     const params = new URLSearchParams(window.location.search);
     const accessToken = params.get('access_token');

     if (accessToken) {
       console.log("URL에서 새 스포티파이 토큰 발견! localStorage에 저장합니다.");
       localStorage.setItem('spotifyAccessToken', accessToken);
       window.history.pushState({}, document.title, window.location.pathname);
       callNewPlaylist(accessToken); //빈 재생 목록 5개 생성 api 호출
       fetchPlaylists();//좋아요 목록 조회 api 호출
     }
   }, []); // [] : 페이지가 처음 로드될 때 *단 한 번* 실행


   // chat 로드 
   useEffect(() => {
     const initialChatId = localStorage.getItem('chatId'); // Login.jsx가 저장한 ID
     if(initialChatId){
       setSelectedChatId(initialChatId);
       }
     else{
       console.warn("로컬스토리지에 chatId 없음, 채팅방 로드 불가");
     }
  }, []);

  //감정 선택
   const handleEmotionSelect = async (emotion) => {
    console.log("emotion:", emotion);
    try {
       const token = localStorage.getItem('accessToken');
       const response = await fetch("http://localhost:5000/api/chat/message", { 
         method: 'POST',
         headers: {
           'Content-Type': 'application/json',
           'Authorization': `${token}` 
         },
         body: JSON.stringify({ emotionName: emotion })
       });

    if (!response.ok) throw new Error('서버 응답 실패');
    const data = await response.json(); 

     // 1. 사용자 메시지 생성
     const newUserMessage = { 
       senderType: true, // (Firestore 기준: true=사용자)
       content: data.user 
       };

     const botMessage = { 
       senderType: false, // (Firestore 기준: false=봇)
       content: data.MUZIGI, 
       recommendTracks: data.recommendTracks,
       emotion: emotion
       };
     setMessages(prevMessages => [...prevMessages, newUserMessage, botMessage]);
   } catch (error) {
      console.error("API 오류:", error);
      const errorMsg = { senderType: false, content: '메시지를 처리하는 데 실패했어요. (콘솔 확인!)' };
      setMessages(prevMessages => [...prevMessages, errorMsg]);
     }
   };

   //렌더링
   return (
     <div className="main-page-container">
       <div className= {`content-area ${isSidebarOpen ? 'sidebar-open' : ''}`}>
         <div className="chat-wrapper">
          <Chat selectedChatId={selectedChatId} messages={messages} setMessages={setMessages}
           setIsFreshLogin={setIsFreshLogin} onToggleLike={handleToggleLike} playlistTracks={playlistTracks}/>
         </div>
         <div className="emotion-wrapper">
           <Emotion onEmotionSelect={handleEmotionSelect} />
         </div>
       </div>

       <Sidebar 
         isOpen={isSidebarOpen} 
         setIsOpen={setIsSidebarOpen} 
         setIsLoggedIn={setIsLoggedIn}
         playlistTracks={playlistTracks}
       />

       {!isSidebarOpen&&(
         <button onClick={()=>setIsSidebarOpen(true)} className='sidebar-open-btn'>
          <FontAwesomeIcon icon={faBars}/>
         </button>
       )}
     </div>
   );
}

export default MainPage;