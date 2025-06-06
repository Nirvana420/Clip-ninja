"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";
import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/hooks/use-toast";
import { extractYouTubeVideoId, secondsToTimeString, timeStringToSeconds } from "@/lib/timeUtils";
import Image from "next/image";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

const youtubeUrlRegex = /^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/;
const timeFormatRegex = /^(?:[0-5]?\d:[0-5]?\d)|(?:(?:\d{1,2}:)?[0-5]?\d:[0-5]?\d)$/;


const formSchema = z.object({
  videoUrl: z.string().min(1, {message: "YouTube URL is required."}).regex(youtubeUrlRegex, "Invalid YouTube URL format. Use youtube.com/watch?v=... or youtu.be/..."),
  startTime: z.string().min(1, {message: "Start time is required."}).regex(timeFormatRegex, "Invalid time format (e.g., MM:SS or HH:MM:SS)"),
  endTime: z.string().min(1, {message: "End time is required."}).regex(timeFormatRegex, "Invalid time format (e.g., MM:SS or HH:MM:SS)"),
}).refine(data => {
  const start = timeStringToSeconds(data.startTime);
  const end = timeStringToSeconds(data.endTime);
  return !isNaN(start) && !isNaN(end) && end > start;
}, {
  message: "End time must be after start time and both must be valid.",
  path: ["endTime"],
});

type ClippedFormValues = z.infer<typeof formSchema>;

export default function ClippedForm() {
  const [videoId, setVideoId] = useState<string | null>(null);
  const [selectedDuration, setSelectedDuration] = useState<string>("00:00");
  const [isLoadingVideo, setIsLoadingVideo] = useState(false);
  const { toast } = useToast();

  const form = useForm<ClippedFormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      videoUrl: "",
      startTime: "00:00",
      endTime: "00:00",
    },
    mode: "onChange",
  });

  const { watch, setValue } = form;
  const startTime = watch("startTime");
  const endTime = watch("endTime");
  const videoUrl = watch("videoUrl");

  useEffect(() => {
    const startSeconds = timeStringToSeconds(startTime);
    const endSeconds = timeStringToSeconds(endTime);

    if (!isNaN(startSeconds) && !isNaN(endSeconds) && endSeconds > startSeconds) {
      setSelectedDuration(secondsToTimeString(endSeconds - startSeconds));
    } else {
      setSelectedDuration("00:00");
    }
  }, [startTime, endTime]);
  
  const handleLoadVideo = () => {
    const currentUrl = form.getValues("videoUrl");
    if (!currentUrl) {
      form.setError("videoUrl", { type: "manual", message: "YouTube URL is required."});
      return;
    }
    const extractedId = extractYouTubeVideoId(currentUrl);
    if (extractedId) {
      setIsLoadingVideo(true);
      setVideoId(extractedId);
      // Simulate video load time
      setTimeout(() => setIsLoadingVideo(false), 1000); 
    } else {
      form.setError("videoUrl", { type: "manual", message: "Invalid YouTube URL. Please check and try again."});
      setVideoId(null);
    }
  };

  function onSubmit(data: ClippedFormValues) {
    toast({
      title: "Clip Download Initiated (Mock)",
      description: `Downloading clip of ${videoId} from ${data.startTime} to ${data.endTime}. This is a placeholder.`,
    });
  }

  return (
    <Card className="w-full max-w-2xl shadow-2xl">
      <CardHeader>
        <CardTitle className="text-3xl font-headline">Create Your Clip</CardTitle>
        <CardDescription>Enter a YouTube URL, select your time range, and download the clip.</CardDescription>
      </CardHeader>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="flex flex-col">
          {/* Part 1: URL Input and Load Video */}
           <div className="px-6 py-4 mb-2"> {/* Adjusted padding/margin as needed */}
            <div className="flex flex-col sm:flex-row gap-2 items-start">
              <FormField
                control={form.control}
                name="videoUrl"
                render={({ field }) => (
                  <FormItem className="flex-grow">
                    <FormLabel>YouTube Video URL</FormLabel>
                    <FormControl>
                      <Input 
                        placeholder="https://www.youtube.com/watch?v=..." 
                        {...field} 
                        className="focus-visible:ring-0 focus-visible:ring-offset-0"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button type="button" onClick={handleLoadVideo} className="mt-0 sm:mt-8 w-full sm:w-auto" disabled={isLoadingVideo || !form.formState.dirtyFields.videoUrl || !videoUrl}>
                {isLoadingVideo ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                Load Video
              </Button>
            </div>
          </div>

          <Separator className="mb-6" />

          {/* Part 2: Video Preview, Time Selection, Duration, and Download */}
          <CardContent className="pt-0">
            <div className="space-y-6">
              {isLoadingVideo && (
                <div className="aspect-video w-full bg-muted rounded-lg flex items-center justify-center">
                  <Loader2 className="h-12 w-12 animate-spin text-primary" />
                </div>
              )}
              {!isLoadingVideo && videoId && (
                <div className="aspect-video w-full rounded-lg overflow-hidden shadow-md">
                  <iframe
                    width="100%"
                    height="100%"
                    src={`https://www.youtube.com/embed/${videoId}`}
                    title="YouTube video player"
                    frameBorder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                  ></iframe>
                </div>
              )}
              {!isLoadingVideo && !videoId && (
                 <div className="aspect-video w-full bg-muted rounded-lg flex items-center justify-center overflow-hidden" data-ai-hint="video placeholder">
                   <Image src="https://placehold.co/560x315.png" alt="Video preview placeholder" width={560} height={315} className="object-cover"/>
                 </div>
              )}

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="startTime"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Start Time</FormLabel>
                      <FormControl>
                        <div className="flex items-center relative">
                          <Input placeholder="MM:SS or HH:MM:SS" {...field} className="w-full"/>
                          <span className="absolute left-2 top-1/2 -translate-y-1/2 pointer-events-none text-muted-foreground">:</span>
                        </div>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="endTime"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>End Time</FormLabel>
                      <FormControl>
                        <div className="flex items-center relative">
                          <Input placeholder="MM:SS or HH:MM:SS" {...field} className="w-full"/>
                           <span className="absolute left-2 top-1/2 -translate-y-1/2 pointer-events-none text-muted-foreground">:</span>
                        </div>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <div>
                <h3 className="text-lg font-medium">Selected Duration</h3>
                <p className="text-2xl text-primary font-bold">{selectedDuration}</p>
              </div>
              
              <Button type="submit" className="w-full" size="lg" disabled={!videoId}>
                Download Clip
              </Button>
            </div>
          </CardContent>
        </form>
      </Form>
      <CardFooter>
        <p className="text-xs text-muted-foreground">
          Note: Actual video download functionality is complex and may be subject to YouTube's Terms of Service. This is a UI demonstration.
        </p>
      </CardFooter>
    </Card>
  );
}
