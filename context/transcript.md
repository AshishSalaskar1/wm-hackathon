Wipro Connect - HVE Workshop prep-20260414_124748-Meeting Recording
April 14, 2026, 7:17AM
45m 41s

Pinki Dutta started transcription

Pinki Dutta   0:04
Because we have a number of prerequisites, and since we have the extended team from you here also, we'll start off with what are the bare minimum things that we need, like a VS Code or GitHub Copilot? How is the usage over there? What are the few things that you have in your environment?
What is the AI usage that you have? So let's walk through that and then focus on.
a more detailing of the problem statement because that's what we want to do a fine tuning on, right? To come to the actual problem that we are solving accompanied by what is the outcome as I have been talking about it, right? What are the outcomes that is in your mind? And then we club together and make it as a structured one.

Rupali Agarwal   0:38
Mmhmm.

Pinki Dutta   0:51
Right, and since you would be the product owner, and I'm thinking this team team from Wipro has almost majority of developers, and you are the PO for the product owner from your side, so this is mainly what the composition would be, but please correct us if I'm missing anything.

Rupali Agarwal   0:51
Okay.
Yes.
No, no, that is correct. That is correct. This is the entire team composition, right? Until, unless you have some other requirement from the team, this is this is our team which will be working on it.

Pinki Dutta   1:22
Okay, okay. So any UI, UX requirement or might be end user, like the personnel who would be using the solution, do we need to talk to them or you would be representing some of their, like the recruiters who are using them on the ground, who are using this solution on the ground today manually or?
Joanne, tomorrow when we propose that and you build that, you know, we help you, you know, with...
What would the solution look like? Who would be the consumers of this solution? Like who would be driving this solution? Would it be only the recruiters or would it be somebody else? So wanted, although you had given us the challenges, but anything on the ground that we need to be aware of.
is also good to have. So either you prefer, you can be present, or if you want to get one of the recruiters or anybody. But yeah, let us know.

Rupali Agarwal   2:15
The CI.
Beat.
Big Pinki.
We can get that, but I think more than the recruiters, it will be internal team. So probably project managers, account managers who have the open roles and who are looking to fill that roles internally rather than going out to external recruiters or looking for external profile.
So I can do one thing, we can have an internal connect to understand how currently these people are kind of going ahead and looking for the roles and try and understand that problem also. And do they need any UI UX front end for this purpose?

Pinki Dutta   2:57
Yeah.

Rupali Agarwal   3:02
We'll try and figure that out as well as we progress.

Pinki Dutta   3:05
Yeah, so one of the important aspects and the reason I'm asking you this is one of the important aspect of this hyper velocity driven engineering ways that we work on is shaping the problem in the right manner, right, with the right parameters in it. And this would play a very important role.

Rupali Agarwal   3:20
Mhm.
Mhm, mhm.

Pinki Dutta   3:25
you know, and doing it in a faster and organized manner using design thinking and so on and so forth. So we mentioned on those lines last yesterday that we would love to see our demo working like of what happens so that we are aware of the workflow and we get acquainted with the workflow that will be easier because we are seeing something.

Rupali Agarwal   3:25
Okay.
And.

Pinki Dutta   3:47
That's one thing and the 2nd is, you know, some sample or resumes and JDs if you could share.

Rupali Agarwal   3:55
Mhm, OK.

Pinki Dutta   3:55
That would be good to have.

Rupali Agarwal   3:57
OKOK.

Pinki Dutta   3:57
And maybe today, tomorrow, or today, if not possible, by tomorrow, if we can see our demo, that would be fantastic to align with our thoughts and that we are not missing on anything.

Rupali Agarwal   4:04
Okay.
Yeah, OK, so.

Pinki Dutta   4:08
And that will also help us to define what are the metrics that we want to measure, like the success criteria and all this stuff, right? So those are the things which we'll be following.

Rupali Agarwal   4:15
MM mm.
Okay, so demo, we can do it tomorrow. Anything related to workplace, workspace, you want to see or you want to understand, that can be done today. And you, Rishab can take you through whatever workspace looks like.
what all tools we use. So if that is needed, we can do it today itself.

Pinki Dutta   4:42
Fantastic. So why not start with that? Shinoj, are you okay? We start with that to understand one part of it. If you have to organize our HP stuff and then we get in slowly into the problem statement and we know tomorrow we have a demo also for that.

Rupali Agarwal   4:44
Yeah.

Shinoj Zacharias   4:56
No, let's start with the problem statement. I think that is that will require a little more discussion and what we really wanted to do in the workshop, right? So that is what we can start. I think workspace and other things we can see tomorrow because it depends on the use cases, what needs to be built, all the things will be it will evolve, right? So I think.

Pinki Dutta   5:14
So.

Rupali Agarwal   5:14
Mhm.

Shinoj Zacharias   5:15
We should start with, we know the problem statement, but little bit of refinement on the problem statement. That's what we should focus today.

Rupali Agarwal   5:19
Hmm.

Pinki Dutta   5:22
Yeah, you start off Shinoj. Yeah, start off Shinoj and I will also, you know, Rupali can express and the team is here can express our thoughts on this. Yeah, go ahead.

Shinoj Zacharias   5:23
Yeah.

Rupali Agarwal   5:23
Okay.

Shinoj Zacharias   5:29
Yeah, OK. Yeah, I think I think we have, you know, the problem statement that we, you know, understood in from yesterday's and the previous meetings, and I think I think everyone in the call was also probably present, but otherwise, very high level, it is all about...

Rupali Agarwal   5:31
Yes.

Shinoj Zacharias   5:49
Given a job description, how do we retrieve very relevant resumes that matches the job description? That is a main problem statement at a very high level, right? So, currently, what we also discussed is that we are considering this as a...
internal, you know, sourcing the resume from the internal Wipro database, database or sources that will, let's call it that, right? So you have a set of resumes internal, we are not just talking about external it, so let's focus on internal. And the hiring manager or project manager or any of those.

Rupali Agarwal   6:16
Mm.
Yeah.
Mhm.

Shinoj Zacharias   6:29
personas is going to, let's say they have a job description, they are going to use the job description, you know, there may be some, you know, way to interact. And for that job description, the solution should find, retrieve all the relevant resume miss for the job description.
Is that the correct statement, Rupali?

Rupali Agarwal   6:50
Yeah.
Yes, it is.

Shinoj Zacharias   6:54
Okay, so if this is the statement, let's look at a few things right now. So the one of the, you know, understanding that we had from the previous call was you had built something internally for this one and there was a performance issue. That is a real reason that we wanted to.

Rupali Agarwal   6:57
Mm.
Mm-hmm.

Shinoj Zacharias   7:13
See how we can make it a performant and scalable solution in the workshop.

Rupali Agarwal   7:18
So, okay, let me clarify more around it. That internal solution which has been built is primarily focusing on the external part, right? Getting the JDs and getting the resumes for external hiring.

Shinoj Zacharias   7:23
Mhm.
Okay, got it.
Got it. So we don't need to... Okay. Go ahead. Sorry.

Rupali Agarwal   7:37
Okay, so...
Yeah, go ahead, go ahead.

Shinoj Zacharias   7:42
So yeah, understood. So we don't need to no way tie to that implementation here. It is a fresh from the ground up. We want to create a solution. Am I correct in this? Yeah.

Rupali Agarwal   7:52
No, one second, one second. Let me elaborate that part also. So that is that solution, what it does it, it has a structured JD kind of a thing. And some recruiter has to upload 100, 200, whatever resume is there, or they can just
pick it from some database and they will scan all those 200 resumes and give a ranking.

Shinoj Zacharias   8:18
Yeah.

Rupali Agarwal   8:19
based on the match criteria. This is only the screening part. For our solution, what we are saying, there is the JD also may not be very structured. It is only role location, skills kind of things in the open roles. And the employee databases there, which is almost like 1,50,000 databases there, which has
Primarily, again, skills are there. Primary skills, secondary skills are there. Some project details are there. Role locations are there. Now I have this open role and I want to scan my entire database.
and then kind of present top 10, 20 ranking based on my match criteria. Correct?

Shinoj Zacharias   9:06
Got it, got it.

Rupali Agarwal   9:07
Now the problem statement are two, there are two parts to it. One is after I got a refined list of suppose 500 resumes, I scan those. But prior to that, how do I come from 1,50,000 to 500,000?
500 items so that I don't have to screen or scan that entire database again and again for each of the rows.
Right, because if I if I go to my existing solution, it will not it will not kind of do that filtering thing. It will pick each role, JD, and it will pick each profile and it will kind of start matching it, right? So, in that case, I have to go through all 1,50,000.
Theoretically.
Right? This is not what I want you to do.

Shinoj Zacharias   10:01
Got it.
The.

Rupali Agarwal   10:05
my available pool also. So that when I come to the screening part, I only have very limited available pool to screen.
So the existing solution can come handy when I have that limited pool and now I want to do the scanning or screen.
It can be part of our solution, but only at a later stage.

Shinoj Zacharias   10:28
Got it.
Okay, we'll see. We will look at that one. Someone can provide a demo of that one tomorrow or day after. That's okay. We'll take a look at it. Yeah, understood. So.

Rupali Agarwal   10:32
We will look at that.
Yeah.
Absolutely. And like, like it is open. If you feel we want to use that, we are open to that. If we feel, you know, the way we have designed our solution is so unique that we don't even need to go to that solution, we are fine with that also. Right?

Shinoj Zacharias   10:52
Got it. Yeah, this is a one implementation approach that you already have. We'll look at, you know, if there are other implementation approaches and other things that we can also explore. Fine, that is okay. Okay. Okay, so two things in this context, right? You said JD and assumes.

Rupali Agarwal   11:02
Absolutely, absolutely. That is what I meant, yeah.

Shinoj Zacharias   11:11
Our assumption here is that both of them are going to be very unstructured.

Rupali Agarwal   11:18
Absolutely. That is what I'm saying. That is the real difference between external when we are going to the internal profile which we are trying to match.

Shinoj Zacharias   11:19
Okay, fine.
Okay, are you saying then externality is a kind of structured receive miss?

Rupali Agarwal   11:31
Yeah, because if I am applying for a job, I'll put my resume. I'll not just put the skills role location, right? I'll put, I'll have one page or two page resume and then I'll apply to any company. While if it is an internal, it will be just my skill role location because I assume rest of the thing is kind of known by the system or

Shinoj Zacharias   11:41
And.
Got it.

Rupali Agarwal   11:51
It's already existing or whatever. But I may not put so much of effort of creating a resume for myself and giving it to the hiring manager, right?
So, so that is the difference, yeah.

Shinoj Zacharias   12:02
Okay.
Sure, go ahead, Deepthi.

Deepthi Sebastian   12:07
So input in this case is not a job description, but rather it is search parameters, right?
separate search parameters like something that talks about skills, something that talks about location, years of experience, something like that, but not a completed job description.

Rupali Agarwal   12:25
Ultimately, JD and resume is also regarding the search and screen and scan parameters also, right? If you want to break it down to that level, it will, it's that only. Probably from JD also, you may be picking a few top parameters against which you want to match your resume.
Right? Here it is not too many words are there in your JDs. It is just, yes, exactly.

Deepthi Sebastian   12:47
Yo.
These are shorter search strings and parameters that you're passing, rather than an entire semi-structured JD that is normally created. Instead of creating those JDs, project managers or other sourcing people, like internal people, they just send these or use these search strings and parameters.

Rupali Agarwal   12:56
Yes.
Yeah.

Deepthi Sebastian   13:11
which are like pretty short like phrases and so on. Okay, okay, okay. Yeah, thank you.

Rupali Agarwal   13:12
Correct, yes.

Shinoj Zacharias   13:17
Yeah, but do we have to, I think we might need to probably support both of them. I think a hiring manager can just upload the JD and we extract what is relevant, all the things, right? So what you're saying is that we might need to support both these approaches. One is upload the JD, the other one is, yeah.

Rupali Agarwal   13:23
Exactly, exactly.
Yes.
Yes, and...
See, I don't see.
I don't see two different ways because if I'm able to pick the top relevant things, right? So whether it comes in a paragraph to me or it's just come those top key parameters, both ways it should be fine for me. Ultimately from the paragraph also, I need to pick those only, the relevant one point, right?

Shinoj Zacharias   13:49
Yeah.
Yeah, but then, but the what is relevant depends on the persona, right? See, sometimes relevancy might differ from.

Rupali Agarwal   14:00
That I need to, that I need to build in the system, see that that I cannot leave on how it is uploaded, right? How the input is given to me, that kind of intelligence I have to build in the system.

Shinoj Zacharias   14:11
Yeah, but now consider that there are there are possibilities two ways. One is a completely JD can be provided and solution can do to the resumes or the other way is that even if in the future you're providing a chat interface where the recruiter should be able to type in something like give me the resume is that the give me the candidate who has you know.
DSM experience in those, so and so field kind of things, so we should think about to these two channels of interactions.

Rupali Agarwal   14:40
Say, if you want, we can start with any one of them. I am fine. And we can then move to make it more complex, right? And cater to the other one also. But as a starting point, anyone we can pick and start with that.

Shinoj Zacharias   14:46
Okay.
Understood.
Yeah, I was looking at not for the real, the workshop, but workshop we need to get a slice of that. But overall, in the future also, when you build this complete solution, you might provide. Okay, got it. Yes, Tagan.

Rupali Agarwal   14:59
Mhm.
Yeah, yes.
Yes, yes.

Pinki Dutta   15:05
Shinoj, I would suggest, yeah, let's look at a very simple one to start with, right? Yeah.

Shinoj Zacharias   15:10
No, understood, understood. The Pinki I understood for the use case that we are planning for the workshop, yes, we should take one slice of this not everything. So I am trying to understand when you really build this solution, when we probably build this solution up in, let's say, in the next three months, what are the channels of interaction? What's the way they actually, every person has interact with this? Yeah.

Rupali Agarwal   15:10
Got it, good.

Pinki Dutta   15:13
No.
Correct, correct, correct.
Absolutely.
And that's where I also mentioned the UI, UX and chat and all those stuff which can come later, but good to know it where you can plug it later in the solution. We give our directions one sec. But having said that, sorry, Shinoj, I'll take a minute. Rupali, the sample would be good to know as we are talking about it more.

Shinoj Zacharias   15:29
Uh, Ginette, good.
Correct, correct.

Pinki Dutta   15:50
We are trying to visualize how it would look like. So if you have something handy, do share it with us on this chat.

Rupali Agarwal   15:56
Approver.

Pinki Dutta   15:58
some of the sample JDs and resumes, which then we can align to what we are talking right now.

Rupali Agarwal   15:58
Oh.
Yeah.
May not be, I may not be having anything handy. Rishab, do you have anything right now to share on the chat or else then we'll have to get back to the team? Probably.

Rishabh Mehrotra   16:16
I guess we need to get back to the team Rupali. We need to just gather it from.

Rupali Agarwal   16:18
Okay, okay.
Yeah, yeah.
Yeah, so Pinki will get back to you on that. Right now we don't have anything handy.

Pinki Dutta   16:29
Okay. Yeah, tomorrow if you can share it, that would be good. During the call when we are seeing the demo, then it would be good to see the sample. So if you can showcase it just on the screen also, that's fine.

Rupali Agarwal   16:30
Yeah.
Yeah.
Mhm.
Exactly.
Okay, okay.

Pinki Dutta   16:42
Okay, during the, if you can show us a demo along with some of those, that would be good. Over to you, Srinivasan. Yeah, if you want to continue your thoughts, Srinivasan. I just wanted to emphasize on this part.

Rupali Agarwal   16:48
Yeah.

Jahan J   16:55
Right, I will ask my question now. I assume the users on the system is going to be like recruiters and the hiring manager, right? And Rupali, so let's say when a JD is posted today, this moment, when do you expect the matches to arrive for that JD?

Rupali Agarwal   17:15
No, in the sense, well, I didn't understand the question. Can you elaborate?

Jahan J   17:19
So as a hiring manager, let's say if I post a JD today and you'd want to get the top 500 matches, right? That's the kind of the ask, right? When you do, how long do you...

Rupali Agarwal   17:22
Uh-huh.
Pinki.
Mm.
Yeah.

Jahan J   17:33
Can, or would you want this find it? Uh, it can take before this find it appears for the for the real time, is it?

Rupali Agarwal   17:37
First time.
Real time. Yes, I want it real time.
That is the challenge I want to solve.

Shinoj Zacharias   17:49
Yeah, it is a near, okay, I don't understand real time, but what is the SLA that you have? For example, if you'd say, you know, it cannot take more than one minute, right? But you will have a limit because you can say, okay, as long as it takes that, let's say 30 seconds is still okay, right? So do you have something on your mind on the SLA for this one?

Rupali Agarwal   17:49
Account.
Yeah.
Okay.
And.
Nathan.
Yeah.
Not really, that I have not defined that SLA because in my mind it is like I have the input, I have the database in which I have to search. So as fast as my system allows me.

Jahan J   18:22
Okay, so what you're actually asking is the JD will have some skills, some ask of these tools and these things. You simply want to match those tools with the structured data of the internal employees. Is it?

Rupali Agarwal   18:35
Look come again.

Jahan J   18:37
So what I understand is the internal employee database already has some structured information like their skills, their tools, those kind of things, right? And what you're also telling us, JD will also have very similar information. And what you're asking is extract that information from JD.
And then simply do a lookup of which employee matches the skill.

Rupali Agarwal   18:57
Mhm.
The.
So it is not a simple lookup, right? Yeah, it is not the keyword search kind of a thing I'm looking at, right? It is more of a contextual semantic match, not just one keyword search, right?

Jahan J   19:03
Okay.

Shinoj Zacharias   19:19
Correct, yeah.

Rupali Agarwal   19:19
That won't be a real challenge which I'm trying to solve. It has to be a contextual match and not just on one parameter, multiple parameters, getting the context. So it is like when a recruiter has a JD and a resume, how that match happens.
Wednesday.

Jahan J   19:42
Mhm.

Rupali Agarwal   19:42
It is not just one keyword, right? It should not be. It should not be one keyword. So it has to be a proper screening of the requirement versus the profile.

Jahan J   20:03
Right.
A and.

Shinoj Zacharias   20:10
Student.

Jahan J   20:10
And...

Rishabh Mehrotra   20:10
To add Shinoj and Jahan, as in, see, as in when you say, see the JD, it's not like a structured kind of data. You'll see it's in a paragraph kind of thing. So similar, you'll have a, it's just a limit, I'm telling you, like it would be a kind of paragraph in both JD as well as you can think of a resume also.

Shinoj Zacharias   20:24
Right.

Rishabh Mehrotra   20:29
You have to parse that, and based on the parsing when you are doing it, how it is taking afterwards, like, and then that part of when when it is it has been parsed and how quickly we can get that data, like list of matching data of the resume is from that JD, so that is something which we are looking out to go for correct Rupali.

Rupali Agarwal   20:50
Yeah, absolutely.

Shinoj Zacharias   20:52
Understood, yeah.

Jahan J   20:53
And let's say after two days after the JD is posted, the employee can update the resume, the skills, et cetera, right? And if after that updation, if that matches a particular JD, how do you want the JD, the matches to be reflected?

Rupali Agarwal   21:12
See, see, that is like if today I'm looking at a GD and the profiles. So based on current information, I have given the match to the hiring manager. Now after today something has changed. I, without rerunning that thing, I cannot get that latest information, right? And it is not feasible to keep on rerunning this thing again and again.

Jahan J   21:30
Mhm.

Rupali Agarwal   21:34
Correct. So there will be a frequency, there will be a time period when I'll kind of rerun for one particular JD. Right. So suppose what I'm trying to say is today's requirement has come. I have run my database and given top 50 searches, top 50 ranked profile.
And out of that, the hiring manager couldn't find anything, right? So probably I have to go back to my system and again run through that database and give the next 50 or something like that. And in the meantime, if some profile has changed, right? So depending on how I have designed my system, if I have excluded that profile, then it is not gonna.
Get included in my searches again, but if I'm starting from fresh, because it is not too much of a load on the system, then it will automatically come as a new search in my in my against my open role, right?

Jahan J   22:33
So you want this match to happen like on a manual basis. You don't want some automatic background matches happening.

Rupali Agarwal   22:42
No, it can be automatic, right? So our role has come today. I have run my database, I have given top 50 rank or whatever is the request, top 50 I have kept and given, next 50 I have kept it in the system itself, the matches, or top 100 I have given.
I have given that list to the hiring manager. Now after two days, five days, the hiring manager again came to the system and again asked, it may be the same role or it may be the new role, right? Then again, it can kind of continue with that searches.
Manuj has joined.

Shinoj Zacharias   23:23
Annoup.

Ankit Manjrekar   23:24
No, how can I'm just wondering how can somebody be on a meeting without being on video?

Rupali Agarwal   23:25
Hi.
I am Aniruddha.

Pinki Dutta   23:32
In OneNote.

Ankit Manjrekar   23:32
So many people on call with no video.

Rupali Agarwal   23:36
Yeah.

Pinki Dutta   23:38
Yeah, you.

Ankit Manjrekar   23:38
No problem, you can go.

Pinki Dutta   23:39
Hey, manojmadhusudhanan, good to see you. So, yeah.

Ankit Manjrekar   23:42
Hey, hey.
I only had seen a lot of mails from you, Pinki, and then nice to see you now.

Rupali Agarwal   23:48
Yeah.

Pinki Dutta   23:49
Yeah.

Rupali Agarwal   23:50
Yeah.

Pinki Dutta   23:52
Huh.

Ankit Manjrekar   23:52
No problem, you guys carry on, yeah, yeah, yeah.

Rupali Agarwal   23:54
Yeah, OK. Thanks, thanks.

Pinki Dutta   23:54
Thank you.

Rupali Agarwal   23:58
Yeah, uh, so...
So the automation can be there, right? But I couldn't understand what kind of automation you are talking about. Is it that for any open role, automatically system should pick that open role and start matching against that role and...
Provide the list, or you are saying...

Jahan J   24:23
I'm kind of coming from an angle of, you know, should the matches be pre-computed and whenever the recruiter wants to look at the top 10, top 20, you just fetch the, give the matches or should the matches happen in real time? So that's kind of the thing. Because when it happens in real time versus it happens in the background, let's say background can be triggered in multiple times, right? Let's say if as a...

Rupali Agarwal   24:38
See, see, I, I...

Jahan J   24:47
As an employee, if I update my resume, then the job can be triggered to rerun the matches. If I, as a hiring manager, if I update the JD, then again I can rerun the matches in the background and then, you know, get the top 50, 100, whatever.

Rupali Agarwal   24:57
Yeah.
Mm.

Jahan J   25:04
Right.

Rupali Agarwal   25:05
Correct, correct. So it's a spot on thing you have told Jahan. I think it has to be a hybrid approach, right? There has to be a background rerunning and a filtering and a bucketing so that we don't have to scan the entire database for each of them.

Jahan J   25:09
Right.
Right.
Right.
Right.
Exactly right, because today if I run the match and nothing has changed, tomorrow if I don't have to run the match again, I can simply fetch the result from the past, right? So.

Rupali Agarwal   25:24
But then, absolutely.
Absolutely. So that background thing, there will be a frequency for that rerunning, right? It could be on a profile getting updated, but that I think won't be feasible because there are huge number of profiles. So it could be a frequency based 15 days in a month or one month frequency.
After that, we will rerun our database, keep those things handy, and as soon as an open role comes, we will kind of do that exact match only on that filtered data.

Jahan J   26:05
Yeah.

Rupali Agarwal   26:07
But it will be time.

Pinki Dutta   26:08
And how many JDs are we talking about Rupali? It's not a single one, right? There will be multiple.

Shinoj Zacharias   26:09
Yeah.

Rupali Agarwal   26:13
No, no, no, absolutely not.

Pinki Dutta   26:16
If I...

Rupali Agarwal   26:17
So many people spending so much of men hours.

Pinki Dutta   26:18
I mean, it's good to quantify, yeah, good to quantify it in terms of when we are doing a scope for this workshop, right? Hence, I'm looking at what's the variability that you want to look at. And as you mentioned, this is helpful, like you run it on a 15 days interval, for example, whenever you...
one is a new requirement is coming in. If it is not per day you are running it or how would those those you know quantifications would be good for us.

Rupali Agarwal   26:46
No, no, she.
No, so there are two things, right? One is background running and one is the requirement-based running. Background running is entirely different. Their frequency does not depend on my open rule, right? Background running is I have kept things ready for somebody to come and use my system.
The front end running, which is when the hiring manager comes with the open role and says, I have this requirement, you give me the top 100 ranked profile, is the need base, right? Is based on the open roles I have in the company as of now.

Pinki Dutta   27:29
Got it.

Rupali Agarwal   27:29
Is that it? Yeah.

Pinki Dutta   27:31
Absolutely.

Rupali Agarwal   27:33
Yeah.

Pinki Dutta   27:34
Deepthi.

Rupali Agarwal   27:35
Deepthi.

Shinoj Zacharias   27:35
Pinki.

Deepthi Sebastian   27:36
What is the underlying system? Is it an HR management system like Workday or SuccessFactors? Is that where all these, you know, talent details are?

Rupali Agarwal   27:49
Yes, it's.

Deepthi Sebastian   27:49
Or is it your own inbuilt? Like, I'm trying to understand the structure. It's a success factor.

Rupali Agarwal   27:51
It's a success factor.
The success factors we have over internal profile.

Deepthi Sebastian   27:56
Okay, so then the way to access this is through APIs. Okay, okay, got it. So it'll be good to like understand in an anonymized way the structure of how your success factors looks like and you know, what are the APIs kind of, yeah, basically the schema of how the resumes are.

Rupali Agarwal   28:00
APIs, yes.
Yes.
Mmh.
Okay.

Deepthi Sebastian   28:17
how talent details are arranged for a particular individual. Yeah. Okay. Thanks.

Rupali Agarwal   28:21
Okay, okay.

Pinki Dutta   28:22
I think Rupali, let's do it tomorrow, then this demo. It will clarify this a lot of doubts for us, preliminary questions, yeah.

Rupali Agarwal   28:26
Yeah.
Okay.
Yeah, so.

Pinki Dutta   28:32
Shinoj.

Shinoj Zacharias   28:34
Are we on the top of the hour or?

Pinki Dutta   28:36
Yeah, we are above time actually, it's 116. So yeah, go ahead please and we'll wrap up with summarizing our key actions.

Shinoj Zacharias   28:39
Yeah, OK, just one.
Yeah.
Yeah, Rupali and Team, the existing system that you said, I think what I heard yesterday or before yesterday is that even for that existing system for matching one JD with all the resumes that you have, it takes.
Two minutes or right 2 minutes, right? And what your expectation now with the new solution is that it has to be near real time and not be real time, but from 2 minutes, if I can, if we can get it to probably let's say under 30 seconds or 40, that itself is a big achievement. Am I?

Rupali Agarwal   29:02
Yes, yes, yes.
Mhm.
It.

Shinoj Zacharias   29:19
Correct in that one.

Rupali Agarwal   29:20
Yes, yes, absolutely. So, so more than from 2 minutes to 30 seconds, whatever is the time, it is more about 1,50 to 200 results. That is the primary problem statement which I am trying to emphasize, right? Which Jahan also mentioned. That background, how do you optimize that background?

Shinoj Zacharias   29:21
Okay.
Okay.

Rupali Agarwal   29:42
database so that you don't scan or screen.

Shinoj Zacharias   29:46
Yeah.

Rupali Agarwal   29:47
this huge database and it is only limited to 200 or 500 screen.

Shinoj Zacharias   29:52
Okay, and the that the existing solution where you got the latency of two minute is for the scanned 200 resumers. Am I correct? Okay.

Rupali Agarwal   30:05
Yes, yes.

Shinoj Zacharias   30:07
OK, there was a hand raised. Anshuman, go ahead. Otherwise, I think we are on the top of the version.

Anshuman Bhadauria   30:14
I had a question, maybe we can have that question in the next meeting as well. I have posted that also because I can see this is like a two tower or maybe two step process, right? We have retrieval and then we have a ranker. So as of today, right, whatever solution we have in production or whatever solution we have developed.

Rupali Agarwal   30:19
Mhm.
Mmh.
Mhm.
Mm-hmm.

Anshuman Bhadauria   30:33
what kind of pain point we are experiencing, right? So I can understand like it's taking time, it has higher latency, right? That's what we are trying to solve. So it's our first part of it, right? Which is refixing the retrieval. It should retrieve 200 candidates in lower latency and those should be semantically relevant candidates.
Is it correct, Rupali?

Rupali Agarwal   30:55
So current system is like you can upload up to 200 resumes and then you can scan or screen those 200 resumes against one open JD or open book, right? And then it is taking around 2 minutes per resume. Correct? Now translate it to my problem.

Anshuman Bhadauria   31:07
Oh.

Rupali Agarwal   31:15
I have 1,50,000 recipes.

Anshuman Bhadauria   31:15
Mhm.

Rupali Agarwal   31:18
what are we going to do about it?

Anshuman Bhadauria   31:21
So, when, when you say, mm-hmm.

Rupali Agarwal   31:21
I cannot upload 1,50,000 resumes and ask it to screen or scan and then sit for days and days for it to give me the results, right?

Anshuman Bhadauria   31:31
No, that I get. So you will basically extract 200 and store it in some database, CS index somewhere, right? So that extraction is already there. And then you will rank it or provide.

Rupali Agarwal   31:33
Yeah.
That 200 which I will screen, I should have that in the background itself, right? Yeah.

Anshuman Bhadauria   31:48
Yeah, yeah, yeah, that is like part of retrieval, like out of millions or maybe 100,000 resumes, right? You'll extract 200 resumes, which is the retrieval part of it, which is the first part. Yeah, second part would be like the ranker, right? You'll rank, maybe use some internal logic to rank those resumes and provide that to hiring manager.

Rupali Agarwal   31:53
Exactly.
Exactly.
Yeah.
Which is the retrieval, yes.
Yes.
Good.

Anshuman Bhadauria   32:07
So in this scope of the problem, right, we'll be focusing on the retrieval part, right, where we have maybe 100,000 resumes and we have to extract relevant, maybe 2,200 resumes and store that into some database or ES index somewhere, right, where we can extract them faster.

Rupali Agarwal   32:10
Mm.
Yep.
Yeah.
Mhm.
Mhm.

Anshuman Bhadauria   32:27
That's the crux of the problem, right?

Rupali Agarwal   32:30
Now, the way you have put it is extract them faster is not, I would put it, I would say, I know this is the 200 resumes where I have to screen, right?

Anshuman Bhadauria   32:42
Mm-hmm.

Rupali Agarwal   32:44
I don't know.

Deepthi Sebastian   32:48
So is it that you have like condensed or compressed the problem into a smaller one for 200, right? You just, instead of the 100,000, you have sort of done a microcosm of it and 200 and within that you want to retrieve as well as rank say 10 or 20 maybe, right? Like something like that.

Rupali Agarwal   32:54
Exactly, exactly.
So, I'll give you, I'll give you an example.
Exactly, exactly. That is that is my problem statement. It's not just fast retrieval. It is that I will not look because it is irrelevant for this open role to kind of.

Anshuman Bhadauria   33:07
Okay, okay, okay.

Deepthi Sebastian   33:09
Okay.
So it's a POC or an MVP kind of thing that you have tried with 200 resumes.

Rupali Agarwal   33:22
No, see that existing system is for entirely different purpose. That is why, because when you go for external hiring, you will have maximum 200, 300 resumes which you will screen, right? So that is entirely focusing on external hiring. It doesn't.

Deepthi Sebastian   33:34
Okay.

Anshuman Bhadauria   33:36
Mhm.

Deepthi Sebastian   33:38
Excellent.
Okay, okay.

Rupali Agarwal   33:41
talk about 10,000. For any open role, you won't see 10,000 resumes also in any company.

Deepthi Sebastian   33:47
Sure, so we have not begun, we have not begun an implementation yet for the internal SuccessFactors based system. Okay, got it, got it. Thanks.

Anshuman Bhadauria   33:49
Mhm.

Rupali Agarwal   33:54
for the internal one.
Yes, yes, we have not.
Yeah.

Anshuman Bhadauria   34:00
Okay.

Shinoj Zacharias   34:02
Just one, God.

Anshuman Bhadauria   34:02
Sure, Rupali. Yeah, we can discuss more on it, the semantic retrieval part. I do get the context here.

Rupali Agarwal   34:06
Mhm, mhm.

Pinki Dutta   34:08
Yeah, Anshuman, hold on to your thoughts. Let's see the demo, then I think things will be much more clear, right, to the questions to the main problem and the secondary problem. So as we suggested earlier, also, we'll take a slice of that one problem and then we will use the HV techniques to address it and see how it works.

Rupali Agarwal   34:14
Yeah.

Pinki Dutta   34:28
And what are the results? Let's see the demo first.

Shinoj Zacharias   34:32
Yeah. And Pinki, I think you might have emphasized multiple times also, the aim of the workshop is that we all together is trying to use HV approaches to build such a solution that is performant and scalable, right? So it is what. So in that one, I know we have a three days, we are trying to.

Anshuman Bhadauria   34:32
Okay, sure.

Pinki Dutta   34:46
S.

Shinoj Zacharias   34:51
get a slice of the problem, that statement that you had, and all of us together work. The way that we are seeing is that with this workshop, you should be able to identify or get an experience of using HV. So in case in the future you want to work on other kind of similar projects, you can, how you can use HV.
techniques to expedite the or improve the productivity. That is the main thing. So here we will focus on this problem statement, use HV approaches and tools and try to build a solution. That is what. So at the end of the things, yes, probably we get a solution or we have a learnings, a lot of learnings that you can take it forward to build a solution.
So hopefully that is what we are focusing on. One more thing I wanted to ask, Rupali, is that the accuracy of the return, whatever the resume is, that is returned, right? That is what, ideally speaking, there is an evaluation techniques that we'll use. It's a data science approach, right? And probably maybe we need to see.
we can address some part of that using HV, probably show one approach, okay, this is how this can be done. Maybe that is not the right approach, but you can still use the HV approaches to try out different approaches, right? So that's how we, I think we should work during these three days of workshop.

Rupali Agarwal   36:02
Mhm.

Pinki Dutta   36:06
So these will be your key takeaways, just to add to what Shinoj is mentioning. So we use the HP to address, structure this problem, give you the ways to solve this problem. We are not building, I mean, deploying anything over here. We are building a sort of prototype and then we are giving you those key evaluation.

Rupali Agarwal   36:09
Mhm.

Pinki Dutta   36:25
framework which will augment this solution and say that, okay, going further, when you deploy it, these are the instruments that you have, which you can use further to make, to enrich it and give it that, you know, the evaluated property, evaluate the solution property. So we will give you those takeaways as well.

Rupali Agarwal   36:42
Mhm.

Shinoj Zacharias   36:42
The.

Rupali Agarwal   36:45
Mhm.

Shinoj Zacharias   36:45
Yeah, even evaluation also is we have to try different approaches. Maybe, you know, it is may not be one solution we can right away find out. I know Anshuman talk, we can talk about a lot of things. They usually try multiple approaches which one work. I think probably Anshuman maybe next meeting we can talk a little bit about that too, right? How that.

Pinki Dutta   36:49
Yeah.

Shinoj Zacharias   37:05
that different approaches that you use for the evaluation framework creations and other things, yeah.

Anshuman Bhadauria   37:10
A short Shinoj.

Pinki Dutta   37:10
So we'll build that agenda, Rupali, and we'll share it during this week itself, discuss it during one of these workshops. And as I mentioned that as we get the, you know, we'll see at the end of the week, what, where are we standing and, you know, what have we achieved and all this stuff in terms of
you know, and then determine, of course, when do we start off with the workshop. And then accordingly, we'll do some of this pre-work during these meetings itself, so that during the three days, since the three days will be limited, we can focus on the main things of building the solution and seeing which of these approaches, the eval framework, what Anshuman would have.

Rupali Agarwal   37:40
Mm.

Pinki Dutta   37:52
Displayed before that, or or spoken to us before that, which of this one do we want to attach to this to to the solution, right? And you want to take away with that.

Rupali Agarwal   38:04
Yeah, OK.

Pinki Dutta   38:07
So, we will do our internal planning and share that with you during the during this week itself.

Rupali Agarwal   38:12
Hey.
That would be good.

Pinki Dutta   38:17
Is that okay, Anshuman, Shinoj, Deepthi?

Anshuman Bhadauria   38:22
Sure, makes sense. We can talk about it and fix it.

Pinki Dutta   38:22
Ohh.
Yeah, let's internally align. Yeah, and then you can get prepped with whatever the approaches that you want to demonstrate and make it, keep it simple. As we are saying, start with a simple problem and then we give them all the, you know, that inputs to enlarge that and get it, make it more complex.
because of the time that we have. So Rupali, then I think we are over time. We will not hold you back. So yeah, let's meet tomorrow at the stipulated at the time that we have. And summarizing, we have shared the team details with you already on the.

Rupali Agarwal   38:51
Hmm.
Yeah.

Pinki Dutta   39:05
on the mail, so hopefully that should help you to get us, get the onboarding started. I will, once you share after this, Paul, if you can share your team details with me, I can start creating the Teams channel and uploading all this logistics part of it, I can start doing. And then we'll internally, tomorrow we let's see the demo from you.

Rupali Agarwal   39:10
Mm-hmm.

Pinki Dutta   39:27
And then we plan all the other HVE workshops and what Rishabh mentioned that, you know, we'll see what are the what what is being used in the environment today, like GitHub Copilot or VS Code or what are the other tooling that is done.

Rupali Agarwal   39:46
Mhm.

Pinki Dutta   39:46
We also see that during this week so that we can plan for the workshops.

Rupali Agarwal   39:51
Yes, sure.

Shinoj Zacharias   39:52
And Pinki, one more thing we can do is that tomorrow, whatever problem statement that we add, whatever context we have, we can actually, you know, keep it in the right, I mean, in a doc or somewhere, we can capture it and then we can circulate to all stakeholders here.

Pinki Dutta   40:04
Absolutely, absolutely. And that's the reason I'm asking for the Teams channel so that we can consider all the information on the Teams documentdocumentURI, which is, you know, which can be used by both the teams.

Shinoj Zacharias   40:10
Yeah.

Rupali Agarwal   40:18
Yeah, yeah, I'll share that.

Pinki Dutta   40:19
Accessible by both the teams, yeah.

Shinoj Zacharias   40:19
Deb.

Rupali Agarwal   40:20
I'll share that right away.

Pinki Dutta   40:22
Yeah, fantastic. Cool. So if there's nothing else, we call it. Deepthi, anything from you before we...

Rupali Agarwal   40:24
Yeah.

Deepthi Sebastian   40:30
No, but tomorrow we are prioritizing the PM's walkthrough, right?

Pinki Dutta   40:36
Yeah, the demo part of it.

Deepthi Sebastian   40:37
That's the demo. Yeah, that'll be great. Like, and then we can go to the next steps. Yeah, that'll be great. Looking forward to it. Yeah. All right.

Rupali Agarwal   40:38
Deb Mobile.
Deb, yeah.

Pinki Dutta   40:41
The demo part of it, yeah, yeah.

Rupali Agarwal   40:43
Yeah.

Pinki Dutta   40:46
Thank you so much. Thanks, everyone, for your time. Have a good rest of the day.

Deepthi Sebastian   40:47
Thank you.

Shinoj Zacharias   40:48
Thank you, bye-bye.

Rupali Agarwal   40:48
Thanks, thanks. Thanks, everyone. Same too. Thanks. Bye.

Ginette Vellera   40:49
Thank you. Bye. Thank you.

Pinki Dutta   40:51
Smite.

Ankit Manjrekar   40:51
Thank you.

Anshuman Bhadauria   40:53
Thank you.

Shinoj Zacharias stopped transcription
