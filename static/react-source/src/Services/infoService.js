
import { doApiCall } from "../Services/utilityService";

const fetchTestimonials = async () => doApiCall({tag_list: [5]},
                                                "content_pages",
                                                "JSON");
export {fetchTestimonials
}